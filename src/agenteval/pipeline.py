"""Evaluation pipeline orchestrator.

Orchestrates the complete evaluation workflow across three tiers:
1. Traditional metrics (execution time, success rate, coordination)
2. LLM-as-a-Judge evaluation (semantic quality assessment)
3. Graph-based complexity analysis (interaction pattern metrics)
"""

from __future__ import annotations

from typing import Any

from agenteval.judges.llm_judge import LLMJudge
from agenteval.metrics.graph import GraphAnalyzer
from agenteval.metrics.traditional import TraditionalMetrics
from agenteval.models.evaluation import Evaluation, Metrics


class EvaluationPipeline:
    """Orchestrates multi-tier evaluation pipeline."""

    def __init__(self, seed: int | None = None, model: str = "mock"):
        """Initialize the evaluation pipeline.

        Args:
            seed: Random seed for reproducibility
            model: LLM model to use for judge evaluation
        """
        self.seed = seed
        self.model = model
        self.traditional_metrics = TraditionalMetrics()
        self.llm_judge = LLMJudge(model=model)
        self.graph_analyzer = GraphAnalyzer()

    def run(
        self,
        traditional_input: dict[str, Any] | None = None,
        llm_judge_input: dict[str, Any] | None = None,
        graph_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run the complete evaluation pipeline.

        Args:
            traditional_input: Traditional metrics input (start_time, end_time, task_results,
                agent_interactions)
            llm_judge_input: LLM judge input (agent_review, baseline_review)
            graph_input: Graph analysis input (interactions list)

        Returns:
            Dictionary with results from all enabled evaluation tiers:
            - traditional_metrics: Metrics object
            - llm_evaluation: Evaluation object
            - graph_metrics: Dictionary of graph metrics
        """
        results: dict[str, Any] = {}

        # Run traditional metrics tier if input provided
        if traditional_input:
            results["traditional_metrics"] = self._run_traditional_metrics(traditional_input)

        # Run LLM judge tier if input provided
        if llm_judge_input:
            results["llm_evaluation"] = self._run_llm_judge(llm_judge_input)

        # Run graph analysis tier if input provided
        if graph_input:
            results["graph_metrics"] = self._run_graph_analysis(graph_input)

        return results

    def _run_traditional_metrics(self, input_data: dict[str, Any]) -> Metrics:
        """Run traditional metrics evaluation.

        Args:
            input_data: Dictionary with start_time, end_time, task_results, agent_interactions

        Returns:
            Metrics object with execution time, success rate, and coordination quality
        """
        execution_time = self.traditional_metrics.calculate_execution_time(
            input_data["start_time"], input_data["end_time"]
        )
        success_rate = self.traditional_metrics.calculate_success_rate(input_data["task_results"])
        coordination_quality = self.traditional_metrics.assess_coordination_quality(
            input_data["agent_interactions"]
        )

        return self.traditional_metrics.create_metrics(
            execution_time=execution_time,
            success_rate=success_rate,
            coordination_quality=coordination_quality,
        )

    def _run_llm_judge(self, input_data: dict[str, Any]) -> Evaluation:
        """Run LLM judge evaluation.

        Args:
            input_data: Dictionary with agent_review and baseline_review

        Returns:
            Evaluation object with LLM judge score and justification
        """
        return self.llm_judge.evaluate(
            agent_review=input_data["agent_review"],
            baseline_review=input_data["baseline_review"],
        )

    def _run_graph_analysis(self, input_data: dict[str, Any]) -> dict[str, float]:
        """Run graph-based complexity analysis.

        Args:
            input_data: Dictionary with interactions list

        Returns:
            Dictionary with graph metrics (density, centrality, clustering)
        """
        interactions = input_data.get("interactions", [])
        graph = self.graph_analyzer.build_graph(interactions)
        return self.graph_analyzer.calculate_all_metrics(graph)
