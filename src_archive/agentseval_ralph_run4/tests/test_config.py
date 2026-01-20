"""Tests for configuration management.

Following TDD approach - these tests should FAIL initially.
Tests validate JSON config loading and runtime configuration.
"""

import json
from pathlib import Path

import pytest

from agenteval.config import load_config
from agenteval.config.config import Config


def test_config_model_structure():
    """Test Config Pydantic model has required fields."""
    config = Config(
        dataset_dir="data/peerread",
        output_dir="output",
        seed=42,
        observability={
            "loguru_enabled": True,
            "logfire_enabled": False,
            "weave_enabled": False,
        },
    )
    assert config.dataset_dir == "data/peerread"
    assert config.output_dir == "output"
    assert config.seed == 42
    assert config.observability["loguru_enabled"] is True


def test_load_config_from_json(tmp_path: Path):
    """Test loading configuration from JSON file."""
    config_file = tmp_path / "test_config.json"
    config_data = {
        "dataset_dir": "data/test",
        "output_dir": "output/test",
        "seed": 123,
        "observability": {
            "loguru_enabled": True,
            "logfire_enabled": False,
            "weave_enabled": False,
        },
    }
    config_file.write_text(json.dumps(config_data))

    config = load_config(config_file)
    assert config.dataset_dir == "data/test"
    assert config.output_dir == "output/test"
    assert config.seed == 123


def test_load_default_config():
    """Test loading default configuration file."""
    config = load_config()
    assert config.dataset_dir is not None
    assert config.output_dir is not None
    assert config.seed is not None
    assert "loguru_enabled" in config.observability


def test_config_validation_fails_on_invalid_seed():
    """Test that Config validates seed is non-negative."""
    with pytest.raises(ValueError):
        Config(
            dataset_dir="data/peerread",
            output_dir="output",
            seed=-1,
            observability={"loguru_enabled": True},
        )


def test_config_has_default_values():
    """Test that Config provides sensible defaults."""
    config = Config()
    assert config.dataset_dir == "data/peerread"
    assert config.output_dir == "output"
    assert config.seed >= 0
