#!/usr/bin/env python3
"""Example: Running the AgentEval evaluation pipeline.

This demonstrates the basic usage of the unified evaluation pipeline
that combines traditional metrics, LLM-as-a-Judge, and graph analysis.
"""

from agenteval.pipeline import EvaluationPipeline
from agenteval.report import EvaluationReport


def main():
    """Run example evaluation."""
    print("=" * 60)
    print("AgentEval - Unified Evaluation Pipeline Example")
    print("=" * 60)
    print()

    # Initialize pipeline with seed for reproducibility
    print("1. Initializing evaluation pipeline...")
    pipeline = EvaluationPipeline(seed=42, enable_tracing=True)
    print("   ✓ Pipeline initialized\n")

    # Prepare example data
    agent_output = """
    The multi-agent system successfully coordinated to solve the task.
    Agent A identified the problem, Agent B processed the data, and
    Agent C synthesized the final solution. The collaboration was
    efficient with minimal redundant communication.
    """

    baseline = """
    The baseline system completed the task with standard performance.
    Each component worked independently with basic coordination.
    """

    interaction_data = {
        "AgentA": {"AgentB": 0.85, "AgentC": 0.72},
        "AgentB": {"AgentC": 0.91},
    }

    # Run evaluation
    print("2. Running evaluation across all three tiers...")
    print("   - Traditional performance metrics")
    print("   - LLM-as-a-Judge semantic evaluation")
    print("   - Graph-based complexity analysis")
    print()

    result = pipeline.run(
        agent_output=agent_output.strip(),
        baseline=baseline.strip(),
        interaction_data=interaction_data,
    )

    print("\n3. Evaluation complete! Generating report...\n")

    # Create and display report
    report = EvaluationReport.from_dict(result)

    print("=" * 60)
    print("EVALUATION REPORT")
    print("=" * 60)
    print(report.summary())
    print()

    # Save report
    output_file = "evaluation_report.json"
    report.save(output_file)
    print(f"✓ Report saved to: {output_file}")
    print()

    # Display key metrics
    print("=" * 60)
    print("KEY METRICS")
    print("=" * 60)
    print(f"Traditional Metrics: {result['traditional_metrics']}")
    print()
    print(f"LLM Evaluation: {result['llm_evaluation']}")
    print()
    print(f"Graph Analysis: {result['graph_analysis']}")
    print()

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
