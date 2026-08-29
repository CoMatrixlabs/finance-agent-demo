"""Runtime settings for the financial-analytics agent.

Baseline is a benign research/market-info assistant: it answers questions from public
research notes and reports generic market status. It holds no client PII and has no
data-export or write capability. Sensitive tools, when added, require human approval.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.2          # low for tool-driving / effectful paths
    max_tool_iterations: int = 6

    require_tool_approval: bool = True        # human-in-the-loop for any write / effectful tool

    log_level: str = "INFO"

    class Config:
        env_prefix = "FINANCE_AGENT_"


settings = Settings()
