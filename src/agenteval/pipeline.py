"""Unified evaluation pipeline orchestrating all three evaluation tiers.

Combines traditional metrics, LLM-as-a-Judge, and graph-based complexity analysis
into a single pipeline with consolidated reporting and observability.
"""

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from agenteval.judges.llm_judge import EvaluationCriteria, LLMJudge
from agenteval.metrics.graph import ComplexityAnalyzer, InteractionGraph
from agenteval.metrics.traditional import (
    CoordinationMetric,
    ExecutionTimeMetric,
    SuccessRateMetric,
)


class PipelineConfig(BaseSettings):
    """Pipeline configuration with pydantic-settings."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    enable_logfire: bool = False
    enable_weave: bool = False
    log_level: str = "INFO"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class EvaluationPipeline:
    """Unified evaluation pipeline combining all three tiers.

    Orchestrates traditional metrics, LLM-as-a-Judge evaluation, and graph-based
    complexity analysis into a single reproducible pipeline.
    """

    def __init__(
        self,
        seed: int | None = None,
        config: PipelineConfig | None = None,
        enable_tracing: bool = True,
    ) -> None:
        """Initialize evaluation pipeline.

        Args:
            seed: Random seed for reproducibility
            config: Pipeline configuration
            enable_tracing: Enable local console tracing
        """
        self.seed = seed
        self.config = config or PipelineConfig()
        self.enable_tracing = enable_tracing

        # Configure logging
        if enable_tracing:
            logger.remove()
            log_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | <level>{message}</level>\n"
            )
            logger.add(
                lambda msg: print(msg, end=""),
                level=self.config.log_level,
                format=log_format,
            )

        # Initialize optional observability integrations
        if self.config.enable_logfire:
            self._init_logfire()

        if self.config.enable_weave:
            self._init_weave()

        # Initialize evaluation components
        self._traditional_metrics = {
            "execution_time": ExecutionTimeMetric(),
            "success_rate": SuccessRateMetric(),
            "coordination": CoordinationMetric(),
        }
        self._llm_judge = LLMJudge(model="test")
        self._graph_analyzer = ComplexityAnalyzer()

    def _init_logfire(self) -> None:
        """Initialize Logfire cloud export (optional)."""
        try:
            import logfire

            logfire.configure()
            logger.info("Logfire cloud export enabled")
        except ImportError:
            logger.warning("Logfire not installed - cloud export disabled")

    def _init_weave(self) -> None:
        """Initialize Weave W&B integration (optional)."""
        try:
            import weave

            weave.init("agenteval")
            logger.info("Weave W&B integration enabled")
        except ImportError:
            logger.warning("Weave not installed - W&B integration disabled")

    def run(
        self,
        agent_output: str,
        baseline: str,
        interaction_data: dict[str, dict[str, float]],
        start_time: float | None = None,
        end_time: float | None = None,
        success: bool = True,
    ) -> dict[str, Any]:
        """Run complete evaluation pipeline.

        Args:
            agent_output: Agent-generated output text
            baseline: Baseline text for comparison
            interaction_data: Agent interaction data for graph analysis
            start_time: Task start time (optional)
            end_time: Task end time (optional)
            success: Whether task was successful

        Returns:
            Consolidated evaluation results

        Raises:
            ValueError: If inputs are invalid
        """
        if not agent_output or not baseline:
            raise ValueError("agent_output and baseline must be non-empty")

        if not interaction_data:
            raise ValueError("interaction_data must be non-empty")

        logger.info(f"Starting evaluation pipeline (seed={self.seed})")

        # Tier 1: Traditional metrics
        logger.debug("Running traditional metrics...")
        traditional_results = self._run_traditional_metrics(
            agent_output, baseline, start_time or 0.0, end_time or 1.0, success
        )

        # Tier 2: LLM-as-a-Judge evaluation
        logger.debug("Running LLM-as-a-Judge evaluation...")
        llm_results = self._run_llm_evaluation(agent_output, baseline)

        # Tier 3: Graph-based complexity analysis
        logger.debug("Running graph-based complexity analysis...")
        graph_results = self._run_graph_analysis(interaction_data)

        # Consolidate results
        results = {
            "traditional_metrics": traditional_results,
            "llm_evaluation": llm_results,
            "graph_analysis": graph_results,
            "metadata": {
                "seed": self.seed,
                "timestamp": datetime.now().isoformat(),
                "pipeline_version": "1.0.0",
            },
        }

        logger.info("Evaluation pipeline completed successfully")
        return results

    def run_batch(self, inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Run pipeline on batch of inputs.

        Args:
            inputs: List of input dictionaries

        Returns:
            List of evaluation results
        """
        logger.info(f"Running batch evaluation on {len(inputs)} inputs")
        return [self.run(**input_data) for input_data in inputs]

    def _run_traditional_metrics(
        self,
        agent_output: str,
        baseline: str,
        start_time: float,
        end_time: float,
        success: bool,
    ) -> dict[str, Any]:
        """Run traditional metrics evaluation.

        Args:
            agent_output: Agent output text
            baseline: Baseline text
            start_time: Start time
            end_time: End time
            success: Success flag

        Returns:
            Traditional metrics results
        """
        results: dict[str, Any] = {}

        # Execution time
        exec_time = self._traditional_metrics["execution_time"].calculate(start_time, end_time)
        results.update(exec_time)

        # Success rate
        success_rate = self._traditional_metrics["success_rate"].calculate(
            total_tasks=1, successful_tasks=1 if success else 0
        )
        results.update(success_rate)

        # Coordination (text similarity)
        coord = self._traditional_metrics["coordination"].calculate_text_similarity(
            agent_output, baseline
        )
        results.update(coord)

        return results

    def _run_llm_evaluation(self, agent_output: str, baseline: str) -> dict[str, Any]:
        """Run LLM-as-a-Judge evaluation.

        Args:
            agent_output: Agent output text
            baseline: Baseline text

        Returns:
            LLM evaluation results
        """
        criteria = EvaluationCriteria(
            aspects=["clarity", "accuracy", "completeness"],
            description="Evaluate the quality of the agent-generated review",
        )

        result = self._llm_judge.compare(agent_output, baseline, criteria)

        return {
            "overall_score": result.overall_score,
            "aspect_scores": result.aspect_scores,
            "reasoning": result.reasoning,
            "justification": result.justification,
        }

    def _run_graph_analysis(self, interaction_data: dict[str, dict[str, float]]) -> dict[str, Any]:
        """Run graph-based complexity analysis.

        Args:
            interaction_data: Agent interaction data

        Returns:
            Graph analysis results
        """
        # Convert interaction data to graph
        interactions = {
            (source, target): {"weight": weight}
            for source, targets in interaction_data.items()
            for target, weight in targets.items()
        }

        graph = InteractionGraph.from_interactions(interactions)

        # Calculate metrics
        metrics = self._graph_analyzer.calculate_all_metrics(graph)

        return metrics
