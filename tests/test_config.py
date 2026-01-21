"""Tests for configuration management."""

from pathlib import Path

import pytest

from agenteval.config.config import load_config


def test_load_config_from_default_json():
    """Test loading configuration from default.json."""
    config = load_config()

    assert config is not None
    assert hasattr(config, "dataset")
    assert hasattr(config, "evaluation")
    assert hasattr(config, "observability")


def test_config_has_dataset_settings():
    """Test that config contains required dataset settings."""
    config = load_config()

    assert hasattr(config.dataset, "name")
    assert hasattr(config.dataset, "source_url")
    assert hasattr(config.dataset, "local_path")


def test_config_has_evaluation_settings():
    """Test that config contains required evaluation settings."""
    config = load_config()

    assert hasattr(config.evaluation, "seed")
    assert hasattr(config.evaluation, "llm_judge_model")


def test_config_has_observability_settings():
    """Test that config contains required observability settings."""
    config = load_config()

    assert hasattr(config.observability, "console_logging")
    assert hasattr(config.observability, "cloud_export")


def test_load_config_from_custom_path(tmp_path):
    """Test loading configuration from custom JSON file path."""
    custom_config = tmp_path / "custom_config.json"
    custom_config.write_text("""{
        "dataset": {
            "name": "test-dataset",
            "source_url": "https://test.example.com",
            "local_path": "data/test"
        },
        "evaluation": {
            "seed": 123,
            "llm_judge_model": "test-model"
        },
        "observability": {
            "console_logging": true,
            "cloud_export": false
        }
    }""")

    config = load_config(custom_config)

    assert config.dataset.name == "test-dataset"
    assert config.evaluation.seed == 123


def test_load_config_raises_on_missing_file():
    """Test that loading non-existent config file raises appropriate error."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("/nonexistent/config.json"))


def test_load_config_raises_on_invalid_json(tmp_path):
    """Test that loading invalid JSON raises appropriate error."""
    invalid_config = tmp_path / "invalid.json"
    invalid_config.write_text("{ invalid json }")

    with pytest.raises(ValueError):
        load_config(invalid_config)
