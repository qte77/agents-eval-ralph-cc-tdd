# Application

## What

A three-tiered evaluation framework for multi-agent AI systems that provides objective benchmarking of autonomous agent teams using the PeerRead dataset

## Why

- Establish foundation with JSON configuration management and shared Pydantic data models to prevent duplication across evaluation modules

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
├── __init__.py
├── models
│   ├── data.py
│   ├── evaluation.py
│   ├── __init__.py
│   └── __pycache__
│       ├── data.cpython-313.pyc
│       ├── evaluation.cpython-313.pyc
│       └── __init__.cpython-313.pyc
└── __pycache__
    └── __init__.cpython-313.pyc
tests/
├── __init__.py
├── __pycache__
│   ├── __init__.cpython-313.pyc
│   ├── test_config.cpython-313-pytest-9.0.2.pyc
│   └── test_models.cpython-313-pytest-9.0.2.pyc
├── test_config.py
└── test_models.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
