# Application

## What

Application description

## Why

- Create JSON config loader and define core Pydantic models (Paper, Review, Evaluation, Metrics, Report) to prevent duplication across evaluation modules

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
├── __init__.py
└── models
    ├── data.py
    ├── evaluation.py
    └── __init__.py
tests/
├── test_config.py
└── test_models.py
```

## Development

Built with Ralph Loop autonomous development using TDD.
