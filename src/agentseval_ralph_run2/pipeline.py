"""Unified evaluation pipeline orchestration.

This module provides a unified pipeline that combines all three evaluation tiers
(traditional metrics, LLM judge, graph metrics) with consolidated reporting
and observability.
"""

import random
import time
import uuid
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field

from agenteval.judges.llm_judge import AgentReview, LLMJudgeAgent
from agenteval.metrics.graph import AgentInteraction, GraphMetricsEvaluator
from agenteval.metrics.traditional import (
    AgentTaskResult,
    CoordinationEvent,
    MetricsEvaluator,
)


class PipelineConfig(BaseModel):
    """Configuration for evaluation pipeline."""

    seed: int | None = Field(default_factory=lambda: random.randint(0, 999999))
    enable_traditional_metrics: bool = True
    enable_llm_judge: bool = True
    enable_graph_metrics: bool = True
    llm_model: str = "test"


class PipelineResult(BaseModel):
    """Result from running the evaluation pipeline."""

    run_id: str
    timestamp: datetime
    config: dict
    traditional_metrics: dict | None
    llm_judge_results: dict | None
    graph_metrics: dict | None
    execution_time: float


class EvaluationPipeline:
    """Unified evaluation pipeline combining all three tiers."""

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize the evaluation pipeline.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.logger = logger

        # Set random seed for reproducibility
        if config.seed is not None:
            random.seed(config.seed)

        # Initialize evaluators
        self.traditional_evaluator = MetricsEvaluator()
        self.graph_evaluator = GraphMetricsEvaluator()
        self.llm_judge = LLMJudgeAgent(model=config.llm_model)

    async def run(
        self,
        task_results: list[AgentTaskResult],
        coordination_events: list[CoordinationEvent],
        interactions: list[AgentInteraction],
        agent_reviews: list[AgentReview] | None = None,
    ) -> PipelineResult:
        """Run the unified evaluation pipeline.

        Args:
            task_results: List of agent task results for traditional metrics
            coordination_events: List of coordination events for traditional metrics
            interactions: List of agent interactions for graph metrics
            agent_reviews: Optional list of agent reviews for LLM judge evaluation

        Returns:
            PipelineResult with consolidated results from all enabled tiers
        """
        start_time = time.time()
        run_id = str(uuid.uuid4())

        self.logger.info(f"Starting evaluation pipeline run {run_id}")
        self.logger.debug(f"Config: seed={self.config.seed}")

        # Initialize result containers
        traditional_metrics = None
        llm_judge_results = None
        graph_metrics = None

        # Run traditional metrics tier
        if self.config.enable_traditional_metrics:
            self.logger.info("Running traditional metrics evaluation")
            trad_metrics = self.traditional_evaluator.evaluate(task_results, coordination_events)
            traditional_metrics = trad_metrics.model_dump()
            self.logger.debug(f"Traditional metrics: {traditional_metrics}")

        # Run LLM judge tier
        if self.config.enable_llm_judge:
            self.logger.info("Running LLM judge evaluation")
            # For testing, create a simple result
            if agent_reviews:
                evaluations = await self.llm_judge.evaluate_batch(agent_reviews)
                llm_judge_results = {
                    "evaluations": [e.model_dump() for e in evaluations],
                    "avg_score": sum(e.score for e in evaluations) / len(evaluations)
                    if evaluations
                    else 0.0,
                }
            else:
                # Default result for testing without reviews
                llm_judge_results = {"evaluations": [], "avg_score": 0.0}
            self.logger.debug(f"LLM judge results: {llm_judge_results}")

        # Run graph metrics tier
        if self.config.enable_graph_metrics:
            self.logger.info("Running graph metrics evaluation")
            g_metrics = self.graph_evaluator.evaluate(interactions)
            graph_metrics = g_metrics.model_dump()
            self.logger.debug(f"Graph metrics: {graph_metrics}")

        execution_time = time.time() - start_time
        self.logger.info(f"Pipeline run {run_id} completed in {execution_time:.2f}s")

        return PipelineResult(
            run_id=run_id,
            timestamp=datetime.now(),
            config=self.config.model_dump(),
            traditional_metrics=traditional_metrics,
            llm_judge_results=llm_judge_results,
            graph_metrics=graph_metrics,
            execution_time=execution_time,
        )
