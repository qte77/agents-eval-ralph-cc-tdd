# Application

## What

Application description

## Why

- Create JSON config loader and define core Pydantic models (Paper, Review, Evaluation, Metrics, Report) to prevent duplication across evaluation modules
- Download PeerRead dataset from source and persist locally with versioning and checksums for reproducibility and offline use
- Load and parse PeerRead dataset from local storage into structured Pydantic models defined in STORY-000

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
├── models
│   ├── data.py
│   ├── evaluation.py
│   └── __init__.py
└── README.md
tests/
├── test_config.py
├── test_downloader.py
├── test_models.py
└── test_peerread.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
