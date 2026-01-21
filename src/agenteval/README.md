# Application

## What

Application description

## Why

- Establish foundation with JSON configuration management and shared Pydantic data models to prevent duplication across evaluation modules.
- Download PeerRead dataset and persist locally with versioning for reproducibility and offline use.
- Load and parse PeerRead dataset from local storage into structured Pydantic models.
- Measure agent system performance with standard metrics for objective comparison of implementations.

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
├── metrics
│   ├── __init__.py
│   └── traditional.py
├── models
│   ├── data.py
│   ├── evaluation.py
│   └── __init__.py
└── README.md
tests/
├── test_config.py
├── test_downloader.py
├── test_models.py
├── test_peerread.py
└── test_traditional.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
