"""Configuration management for AgentEval."""

import json
from pathlib import Path

from pydantic import BaseModel


class DatasetConfig(BaseModel):
    """Dataset configuration."""

    name: str
    version: str
    path: str


class EvaluationConfig(BaseModel):
    """Evaluation configuration."""

    seed: int
    batch_size: int
    llm_judge_model: str


class ObservabilityConfig(BaseModel):
    """Observability configuration."""

    backend: str
    log_level: str


class Config(BaseModel):
    """Configuration model for AgentEval."""

    dataset: DatasetConfig
    evaluation: EvaluationConfig
    observability: ObservabilityConfig


def load_config(config_path: Path) -> Config:
    """Load configuration from JSON file.

    Args:
        config_path: Path to JSON config file

    Returns:
        Config: Parsed configuration object

    Raises:
        FileNotFoundError: If config file does not exist
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config_data = json.load(f)

    return Config(**config_data)
