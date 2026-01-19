# Application

## What

A three-tiered evaluation framework for multi-agent AI systems that provides objective benchmarking of autonomous agent teams using the PeerRead dataset

## Why

- Establish foundation with JSON configuration management and shared Pydantic data models to prevent duplication across evaluation modules
- Download PeerRead dataset and persist locally with versioning for reproducibility and offline use
- Load and parse PeerRead dataset from local storage into structured Pydantic models
- Implement standard metrics (execution time, success rate, coordination quality) for agent system evaluation

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
│   ├── __init__.py
│   └── __pycache__
│       ├── config.cpython-313.pyc
│       └── __init__.cpython-313.pyc
├── data
│   ├── downloader.py
│   ├── __init__.py
│   ├── peerread.py
│   └── __pycache__
│       ├── downloader.cpython-313.pyc
│       ├── __init__.cpython-313.pyc
│       └── peerread.cpython-313.pyc
├── example.py
├── __init__.py
├── metrics
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-313.pyc
│   │   └── traditional.cpython-313.pyc
│   └── traditional.py
├── models
│   ├── data.py
│   ├── evaluation.py
│   ├── __init__.py
│   └── __pycache__
│       ├── data.cpython-313.pyc
│       ├── evaluation.cpython-313.pyc
│       └── __init__.cpython-313.pyc
├── __pycache__
│   └── __init__.cpython-313.pyc
└── README.md
tests/
├── __init__.py
├── __pycache__
│   ├── __init__.cpython-313.pyc
│   ├── test_config.cpython-313-pytest-9.0.2.pyc
│   ├── test_downloader.cpython-313-pytest-9.0.2.pyc
│   ├── test_models.cpython-313-pytest-9.0.2.pyc
│   ├── test_peerread.cpython-313-pytest-9.0.2.pyc
│   └── test_traditional.cpython-313-pytest-9.0.2.pyc
├── test_config.py
├── test_downloader.py
├── test_models.py
├── test_peerread.py
└── test_traditional.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
