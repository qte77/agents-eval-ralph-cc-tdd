"""Tests for configuration loader."""

import json
from pathlib import Path

import pytest
from agenteval.config.config import Config, load_config


def test_config_loads_from_json_file(tmp_path: Path):
    """Test that config can be loaded from a JSON file."""
    config_data = {
        "dataset": {"name": "peerread", "version": "1.0", "path": "data/peerread"},
        "evaluation": {
            "seed": 42,
            "batch_size": 10,
            "llm_judge_model": "claude-sonnet-4",
        },
        "observability": {"backend": "loguru", "log_level": "INFO"},
    }

    config_file = tmp_path / "test_config.json"
    config_file.write_text(json.dumps(config_data))

    config = load_config(config_file)

    assert config.dataset.name == "peerread"
    assert config.dataset.version == "1.0"
    assert config.evaluation.seed == 42
    assert config.observability.backend == "loguru"


def test_config_has_dataset_settings():
    """Test that Config model has dataset configuration."""
    config = Config(
        dataset={"name": "peerread", "version": "1.0", "path": "data/peerread"},
        evaluation={"seed": 42, "batch_size": 10, "llm_judge_model": "claude-sonnet-4"},
        observability={"backend": "loguru", "log_level": "INFO"},
    )

    assert config.dataset.name == "peerread"
    assert config.dataset.version == "1.0"
    assert config.dataset.path == "data/peerread"


def test_config_has_evaluation_settings():
    """Test that Config model has evaluation configuration."""
    config = Config(
        dataset={"name": "peerread", "version": "1.0", "path": "data/peerread"},
        evaluation={"seed": 42, "batch_size": 10, "llm_judge_model": "claude-sonnet-4"},
        observability={"backend": "loguru", "log_level": "INFO"},
    )

    assert config.evaluation.seed == 42
    assert config.evaluation.batch_size == 10
    assert config.evaluation.llm_judge_model == "claude-sonnet-4"


def test_config_has_observability_settings():
    """Test that Config model has observability configuration."""
    config = Config(
        dataset={"name": "peerread", "version": "1.0", "path": "data/peerread"},
        evaluation={"seed": 42, "batch_size": 10, "llm_judge_model": "claude-sonnet-4"},
        observability={"backend": "loguru", "log_level": "INFO"},
    )

    assert config.observability.backend == "loguru"
    assert config.observability.log_level == "INFO"


def test_load_config_raises_on_missing_file():
    """Test that load_config raises FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent_config.json"))


def test_config_loads_default_config():
    """Test that default config can be loaded from src/agenteval/config/default.json."""
    # This will be used at runtime to load default configuration
    default_config_path = Path("src/agenteval/config/default.json")

    # Test will fail until default.json exists
    assert default_config_path.exists(), "default.json must exist"

    config = load_config(default_config_path)

    assert config.dataset is not None
    assert config.evaluation is not None
    assert config.observability is not None
