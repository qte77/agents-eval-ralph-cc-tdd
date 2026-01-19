"""Configuration schema and loader for AgentEvals."""

import json
from pathlib import Path

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Application configuration."""

    dataset_dir: str = "data/peerread"
    output_dir: str = "output"
    seed: int = Field(default=42, ge=0)
    observability: dict[str, bool] = Field(
        default_factory=lambda: {
            "loguru_enabled": True,
            "logfire_enabled": False,
            "weave_enabled": False,
        }
    )


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from JSON file."""
    if config_path is None:
        config_path = Path(__file__).parent / "default.json"

    with open(config_path) as f:
        config_data = json.load(f)

    return Config(**config_data)
