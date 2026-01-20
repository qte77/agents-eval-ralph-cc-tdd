# Quick Start Guide

## Installation

```bash
# Install dependencies
make setup_dev

# Or manually with uv
uv sync --all-groups
```

## Basic Usage

### 1. Run Evaluation Pipeline

```python
from agenteval.pipeline import EvaluationPipeline

# Initialize pipeline
pipeline = EvaluationPipeline(
    seed=42,  # For reproducibility
    enable_tracing=True  # Console logging
)

# Run evaluation
result = pipeline.run(
    agent_output="The agent successfully completed the task with high accuracy.",
    baseline="The baseline approach completed the task adequately.",
    interaction_data={
        "agent1": {"agent2": 0.8, "agent3": 0.6},
        "agent2": {"agent3": 0.9}
    }
)

# Access results
print(result["traditional_metrics"])  # Performance metrics
print(result["llm_evaluation"])       # LLM judge scores
print(result["graph_analysis"])       # Complexity metrics
```

### 2. Generate Report

```python
from agenteval.report import EvaluationReport

# Create report from pipeline results
report = EvaluationReport.from_dict(result)

# Print summary
print(report.summary())

# Save to file
report.save("evaluation_report.json")

# Load from file
loaded_report = EvaluationReport.load("evaluation_report.json")
```

### 3. Load PeerRead Dataset

```python
from agenteval.data.peerread import PeerReadLoader

# Load dataset
loader = PeerReadLoader(source="huggingface", max_samples=100)
dataset = loader.load()

# Iterate in batches
for batch in loader.iter_batches(batch_size=10):
    for pair in batch:
        print(f"Paper: {pair.paper.title}")
        print(f"Review: {pair.review.comments}")
```

### 4. Traditional Metrics

```python
from agenteval.metrics.traditional import (
    ExecutionTimeMetric,
    SuccessRateMetric,
    CoordinationMetric
)
from datetime import datetime

# Execution time
exec_metric = ExecutionTimeMetric()
time_taken = exec_metric.calculate(
    start_time=datetime(2024, 1, 1, 10, 0, 0),
    end_time=datetime(2024, 1, 1, 10, 5, 30)
)
print(f"Execution time: {time_taken} seconds")

# Success rate
success_metric = SuccessRateMetric()
rate = success_metric.calculate(
    total_tasks=100,
    successful_tasks=85
)
print(f"Success rate: {rate:.2%}")

# Coordination quality
coord_metric = CoordinationMetric()
similarity = coord_metric.text_similarity("agent output 1", "agent output 2")
print(f"Text similarity: {similarity}")
```

### 5. LLM-as-a-Judge

```python
from agenteval.judges.llm_judge import LLMJudge, EvaluationCriteria

# Initialize judge
judge = LLMJudge(model="test")  # Use "gpt-4" or "claude-3-5-sonnet-latest" in production

# Define criteria
criteria = EvaluationCriteria(
    aspects=["accuracy", "clarity", "completeness"],
    scale_min=1,
    scale_max=5
)

# Evaluate
result = judge.evaluate(
    agent_output="The agent completed the task successfully.",
    criteria=criteria
)
print(f"Score: {result.score}/5")
print(f"Justification: {result.justification}")

# Compare against baseline
comparison = judge.compare(
    agent_output="Agent implementation",
    baseline="Baseline implementation",
    criteria=criteria
)
```

### 6. Graph-Based Analysis

```python
from agenteval.metrics.graph import InteractionGraph, ComplexityAnalyzer

# Create interaction graph
edges = [
    ("agent1", "agent2", {"weight": 0.8}),
    ("agent2", "agent3", {"weight": 0.9}),
    ("agent1", "agent3", {"weight": 0.6})
]
graph = InteractionGraph.from_edges(edges)

# Analyze complexity
analyzer = ComplexityAnalyzer()
metrics = analyzer.calculate_all_metrics(graph.graph)

print(f"Graph density: {metrics['density']}")
print(f"Clustering coefficient: {metrics['clustering_coefficient']}")
print(f"Hub agents: {analyzer.identify_hubs(graph.graph)}")

# Export for visualization
graph.export_json("interaction_graph.json")
graph.export_graphml("interaction_graph.graphml")
```

### 7. Batch Evaluation

```python
from agenteval.pipeline import EvaluationPipeline

pipeline = EvaluationPipeline(seed=42)

# Multiple evaluations
inputs = [
    {
        "agent_output": "Output 1",
        "baseline": "Baseline 1",
        "interaction_data": {"a1": {"a2": 0.8}}
    },
    {
        "agent_output": "Output 2",
        "baseline": "Baseline 2",
        "interaction_data": {"a1": {"a2": 0.9}}
    }
]

results = [pipeline.run(**inp) for inp in inputs]

# Aggregate results
from agenteval.report import BatchReport

batch_report = BatchReport(evaluations=[
    EvaluationReport.from_dict(r) for r in results
])
print(batch_report.summary())
```

## Configuration

Configure via environment variables or `.env` file:

```bash
# .env
ENABLE_LOGFIRE=false
ENABLE_WEAVE=false
LOG_LEVEL=INFO
```

```python
from agenteval.pipeline import PipelineConfig, EvaluationPipeline

config = PipelineConfig(
    enable_logfire=False,
    enable_weave=False,
    log_level="DEBUG"
)

pipeline = EvaluationPipeline(config=config)
```

## Running Tests

```bash
# All tests
make test_all

# Type checking
make type_check

# Full validation (format + type check + tests)
make validate
```

## Next Steps

- Read the [PRD](docs/PRD.md) for detailed requirements
- Check [test files](tests/) for more usage examples
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
