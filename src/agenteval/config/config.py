"""Configuration loader and models for AgentEval.

Loads configuration from JSON files and validates structure using Pydantic.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class DatasetConfig(BaseModel):
    """Dataset configuration."""

    name: str = Field(..., description="Dataset name (e.g., 'peerread')")
    version: str = Field(..., description="Dataset version")
    path: str = Field(..., description="Path to dataset files")


class EvaluationConfig(BaseModel):
    """Evaluation configuration."""

    seed: int = Field(..., description="Random seed for reproducibility")
    batch_size: int = Field(..., description="Batch size for processing")
    llm_judge_model: str = Field(..., description="Model to use for LLM judge")


class ObservabilityConfig(BaseModel):
    """Observability configuration."""

    backend: str = Field(..., description="Observability backend (e.g., 'loguru')")
    log_level: str = Field(..., description="Logging level")


class Config(BaseModel):
    """Main configuration model."""

    dataset: DatasetConfig
    evaluation: EvaluationConfig
    observability: ObservabilityConfig


def load_config(config_path: Path) -> Config:
    """Load configuration from JSON file.

    Args:
        config_path: Path to configuration JSON file

    Returns:
        Validated Config object

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file contains invalid JSON
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config_data = json.loads(config_path.read_text())
    return Config(**config_data)
