"""Evaluation pipeline orchestrator."""

from datetime import UTC, datetime

from agenteval.config.config import load_config
from agenteval.judges.llm_judge import LLMJudge
from agenteval.metrics.graph import GraphMetrics
from agenteval.metrics.traditional import TraditionalMetrics


class EvaluationPipeline:
    """Orchestrate execution of all evaluation modules in sequence."""

    def __init__(self, seed: int | None = None):
        """Initialize pipeline with optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible runs. If None, uses seed from config.
        """
        if seed is None:
            config = load_config()
            self.seed = config.evaluation.seed
        else:
            self.seed = seed

        # Initialize evaluation modules
        self.traditional_metrics = TraditionalMetrics()
        self.graph_metrics = GraphMetrics()
        self.llm_judge = LLMJudge(use_test_model=True)  # Use test model for no API calls

    def run(self, task_data: dict) -> dict:
        """Run all three evaluation tiers in sequence.

        Args:
            task_data: Dict containing:
                - start_time: datetime
                - end_time: datetime
                - task_results: list[dict]
                - agent_interactions: list[dict]
                - agent_reviews: list[Review]
                - human_baselines: list[Review]

        Returns:
            Dict with results from all modules formatted for reporting:
                - traditional_metrics: dict
                - llm_evaluations: list[Evaluation]
                - graph_metrics: dict
                - run_metadata: dict
        """
        # Extract data for each tier
        start_time = task_data["start_time"]
        end_time = task_data["end_time"]
        task_results = task_data["task_results"]
        agent_interactions = task_data["agent_interactions"]
        agent_reviews = task_data.get("agent_reviews", [])
        human_baselines = task_data.get("human_baselines", [])

        # Tier 1: Traditional performance metrics
        traditional_results = self.traditional_metrics.calculate_all(
            start_time=start_time,
            end_time=end_time,
            task_results=task_results,
            agent_interactions=agent_interactions,
        )

        # Tier 2: LLM-as-a-Judge evaluation
        llm_evaluations = []
        if agent_reviews and human_baselines:
            llm_evaluations = self.llm_judge.batch_evaluate(
                agent_reviews=agent_reviews,
                human_baselines=human_baselines,
            )

        # Tier 3: Graph-based complexity analysis
        graph_results = self.graph_metrics.analyze(agent_interactions)

        # Collect all results for reporting module
        return {
            "traditional_metrics": traditional_results,
            "llm_evaluations": llm_evaluations,
            "graph_metrics": graph_results,
            "run_metadata": {
                "seed": self.seed,
                "timestamp": datetime.now(UTC),
            },
        }
