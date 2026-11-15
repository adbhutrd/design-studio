"""Central configuration for the Open Design Studio.

Every value comes from the environment (see `.env.example`). Nothing here is
required: missing values simply disable the matching provider so the platform
still runs with whatever free tier the user has.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

try:  # optional, so the app also runs without python-dotenv installed
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass(frozen=True)
class Settings:
    # --- LLM / copywriting (Llama) ---
    groq_api_key: str
    groq_base_url: str
    groq_model: str
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    ollama_base_url: str
    ollama_model: str

    # --- Image generation ---
    comfyui_gateway_url: str
    pollinations_url: str

    # --- Image cleanup (rembg + upscale) ---
    cleanup_url: str

    # --- Output ---
    output_dir: str
    request_timeout: float


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build the settings once and reuse them."""
    return Settings(
        groq_api_key=_env("GROQ_API_KEY"),
        groq_base_url=_env("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        groq_model=_env("GROQ_MODEL", "llama-3.3-70b-versatile"),
        openrouter_api_key=_env("OPENROUTER_API_KEY"),
        openrouter_base_url=_env("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        openrouter_model=_env("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free"),
        ollama_base_url=_env("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        ollama_model=_env("OLLAMA_MODEL", "llama3.2"),
        comfyui_gateway_url=_env("COMFYUI_GATEWAY_URL", "http://127.0.0.1:8100").rstrip("/"),
        pollinations_url=_env("POLLINATIONS_URL", "https://image.pollinations.ai/prompt"),
        cleanup_url=_env("CLEANUP_URL", "http://127.0.0.1:8000").rstrip("/"),
        output_dir=_env("OUTPUT_DIR", os.path.join(os.path.dirname(__file__), "outputs")),
        request_timeout=float(_env("REQUEST_TIMEOUT", "600")),
    )
