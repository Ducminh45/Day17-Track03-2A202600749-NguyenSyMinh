from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

from model_provider import ProviderConfig


@dataclass
class LabConfig:
    """Student TODO: define the shared configuration for the lab."""
    base_dir: Path
    data_dir: Path
    state_dir: Path
    compact_threshold_tokens: int
    compact_keep_messages: int
    model: ProviderConfig
    judge_model: ProviderConfig


def load_config(base_dir: Path | None = None) -> LabConfig:
    """Student TODO: load environment variables and return a LabConfig."""
    root = (base_dir or Path(__file__).resolve().parent.parent).resolve()
    
    # Load .env
    load_dotenv(root / ".env")

    state_dir = root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    
    data_dir = root / "data"

    provider_name = os.getenv("LLM_PROVIDER", "custom").lower()
    model_name = os.getenv("LLM_MODEL", "offline-mock")
    
    api_key = None
    base_url = None
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
    elif provider_name == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
    elif provider_name == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    elif provider_name == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
    elif provider_name == "custom":
        api_key = os.getenv("CUSTOM_API_KEY", "dummy")
        base_url = os.getenv("CUSTOM_BASE_URL")

    model_config = ProviderConfig(
        provider=provider_name,
        model_name=model_name,
        temperature=0.0,
        api_key=api_key,
        base_url=base_url
    )
    
    judge_model_config = ProviderConfig(
        provider=provider_name,
        model_name=model_name,
        temperature=0.0,
        api_key=api_key,
        base_url=base_url
    )

    return LabConfig(
        base_dir=root,
        data_dir=data_dir,
        state_dir=state_dir,
        compact_threshold_tokens=int(os.getenv("COMPACT_THRESHOLD_TOKENS", "500")),
        compact_keep_messages=int(os.getenv("COMPACT_KEEP_MESSAGES", "2")),
        model=model_config,
        judge_model=judge_model_config
    )
