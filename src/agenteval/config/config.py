"""Configuration management for AgentEval."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Configuration model for AgentEval."""

    dataset_dir: str = "data/peerread"
    output_dir: str = "output"
    seed: int = Field(default=42, ge=0)
    observability: dict[str, Any] = Field(
        default_factory=lambda: {
            "loguru_enabled": True,
            "logfire_enabled": False,
            "weave_enabled": False,
        }
    )

    @field_validator("seed")
    @classmethod
    def validate_seed(cls, v: int) -> int:
        """Validate that seed is non-negative."""
        if v < 0:
            raise ValueError("seed must be non-negative")
        return v


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from JSON file.

    Args:
        config_path: Path to JSON config file. If None, loads default.json

    Returns:
        Config: Parsed configuration object
    """
    if config_path is None:
        # Load default config from package
        default_config_path = Path(__file__).parent / "default.json"
        config_path = default_config_path

    with open(config_path) as f:
        config_data = json.load(f)

    return Config(**config_data)
