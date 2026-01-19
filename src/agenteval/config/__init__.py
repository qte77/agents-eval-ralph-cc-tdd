"""Configuration management for AgentEvals.

Provides JSON-based configuration loading with Pydantic validation.
"""

from agenteval.config.config import Config, load_config

__all__ = ["Config", "load_config"]
