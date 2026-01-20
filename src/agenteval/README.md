# Application

## What

Application description

## Why

- Create JSON config loader and define core Pydantic models (Paper, Review, Evaluation, Metrics, Report) to prevent duplication across evaluation modules.
- Download PeerRead dataset from source and persist locally with versioning for reproducibility and offline use.
- Load and parse PeerRead dataset from local storage into structured Pydantic models for downstream processing.
- Measure agent system performance with standard metrics (execution time, success rate, coordination quality) for objective comparison.
- Evaluate semantic quality of agent outputs using LLM-based assessment against human baseline reviews from PeerRead dataset.

## Quick Start

```bash
# Run application
python -m agenteval

# Run example
python src/agenteval/example.py

# Run tests
pytest tests/
```

## Architecture

```text
src/agenteval
├── config
│   ├── config.py
│   ├── default.json
│   └── __init__.py
├── data
│   ├── downloader.py
│   ├── __init__.py
│   └── peerread.py
├── example.py
├── __init__.py
├── judges
│   ├── __init__.py
│   └── llm_judge.py
├── metrics
│   ├── graph.py
│   ├── __init__.py
│   ├── traditional_green.py
│   ├── traditional.py
│   ├── traditional_red.py
│   └── traditional_stub.py
├── models
│   ├── data.py
│   ├── evaluation.py
│   └── __init__.py
└── README.md
tests/
├── test_config.py
├── test_downloader.py
├── test_graph.py
├── test_llm_judge.py
├── test_models.py
├── test_peerread.py
└── test_traditional.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
