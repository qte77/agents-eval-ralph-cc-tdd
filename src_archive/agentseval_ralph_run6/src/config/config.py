"""Configuration loader for AgentEval."""

import json
from pathlib import Path

from pydantic import BaseModel


class DatasetConfig(BaseModel):
    """Dataset configuration."""

    name: str
    source_url: str
    local_path: str


class EvaluationConfig(BaseModel):
    """Evaluation configuration."""

    seed: int
    llm_judge_model: str


class ObservabilityConfig(BaseModel):
    """Observability configuration."""

    console_logging: bool
    cloud_export: bool


class Config(BaseModel):
    """Main configuration model."""

    dataset: DatasetConfig
    evaluation: EvaluationConfig
    observability: ObservabilityConfig


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from JSON file.

    Args:
        config_path: Path to config file. If None, loads default.json.

    Returns:
        Config object with loaded settings.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If JSON is invalid or schema validation fails.
    """
    if config_path is None:
        config_path = Path(__file__).parent / "default.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}") from e

    return Config.model_validate(data)
