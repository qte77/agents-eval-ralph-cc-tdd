"""Evaluation pipeline orchestrator.

Orchestrates the execution of all evaluation modules in sequence with
dependency management and reproducibility controls.
"""

from typing import Any

from agenteval.judges.llm_judge import evaluate_review, evaluate_review_batch
from agenteval.metrics.graph import GraphAnalyzer
from agenteval.metrics.traditional import TraditionalMetrics
from agenteval.models.data import Review
from agenteval.models.evaluation import Evaluation, Metrics


class Pipeline:
    """Evaluation pipeline orchestrator.

    Coordinates execution of all three evaluation tiers:
    - Traditional performance metrics (execution time, success rate, coordination)
    - LLM-as-a-Judge semantic quality evaluation
    - Graph-based complexity analysis

    Ensures reproducible runs with seed configuration and manages dependencies
    between evaluation modules.
    """

    def __init__(self, seed: int = 42):
        """Initialize pipeline with reproducibility seed.

        Args:
            seed: Random seed for reproducible evaluation runs
        """
        self.seed = seed

    def run_traditional_metrics(self, traditional_input: dict[str, Any]) -> Metrics:
        """Run traditional performance metrics evaluation.

        Args:
            traditional_input: Dictionary with start_time, end_time, task_results,
                             and coordination_events

        Returns:
            Metrics: Traditional performance metrics results
        """
        metrics = TraditionalMetrics(
            start_time=traditional_input["start_time"],
            end_time=traditional_input["end_time"],
            task_results=traditional_input["task_results"],
            coordination_events=traditional_input["coordination_events"],
        )
        return metrics.calculate()

    def run_llm_judge(
        self,
        agent_review: Review,
        baseline_review: Review,
    ) -> Evaluation:
        """Run LLM-as-a-Judge semantic quality evaluation.

        Args:
            agent_review: Agent-generated review to evaluate
            baseline_review: Human baseline review for comparison

        Returns:
            Evaluation: LLM judge evaluation results
        """
        return evaluate_review(
            agent_review=agent_review,
            baseline_review=baseline_review,
        )

    def run_llm_judge_batch(self, review_pairs: list[dict]) -> list[Evaluation]:
        """Run LLM judge on multiple review pairs.

        Args:
            review_pairs: List of dicts with 'agent_review' and 'baseline_review'

        Returns:
            List of Evaluation results
        """
        return evaluate_review_batch(review_pairs)

    def run_graph_analysis(self, interactions: list[dict[str, Any]]) -> dict[str, Any]:
        """Run graph-based complexity analysis.

        Args:
            interactions: List of agent interaction events with source, target,
                        timestamp, and type

        Returns:
            Dictionary with graph metrics: density, centrality,
            clustering_coefficient, and coordination_patterns
        """
        analyzer = GraphAnalyzer(interactions)
        return analyzer.analyze()

    def run_all(
        self,
        traditional_input: dict[str, Any],
        agent_review: Review,
        baseline_review: Review,
        interactions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Run all three evaluation tiers in sequence.

        Args:
            traditional_input: Input for traditional metrics evaluation
            agent_review: Agent-generated review for LLM judge
            baseline_review: Baseline review for LLM judge
            interactions: Agent interaction events for graph analysis

        Returns:
            Dictionary containing results from all three evaluation tiers:
            - traditional_metrics: Metrics object
            - llm_evaluation: Evaluation object
            - graph_metrics: Dictionary with graph analysis results
        """
        # Run all three evaluation tiers
        traditional_metrics = self.run_traditional_metrics(traditional_input)
        llm_evaluation = self.run_llm_judge(agent_review, baseline_review)
        graph_metrics = self.run_graph_analysis(interactions)

        # Collect and return all results
        return {
            "traditional_metrics": traditional_metrics,
            "llm_evaluation": llm_evaluation,
            "graph_metrics": graph_metrics,
        }
