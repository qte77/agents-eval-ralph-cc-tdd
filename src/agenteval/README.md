# Application

## What

Application description

## Why

- Establish foundation with JSON configuration management and shared Pydantic data models to prevent duplication across evaluation modules.
- Download PeerRead dataset and persist locally with versioning for reproducibility and offline use.
- Load and parse PeerRead dataset from local storage into structured Pydantic models.
- Measure agent system performance with standard metrics for objective comparison of implementations.
- Evaluate semantic quality of provided agent outputs using LLM-based assessment against human baseline reviews from PeerRead dataset.

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
│   └── traditional.py
├── models
│   ├── data.py
│   ├── evaluation.py
│   └── __init__.py
└── README.md
tests/
├── __init__.py
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
