"""LLM layer — writes the marketing headline and the image prompt.

Provider order (first one configured/reachable wins):
  1. Groq        (free API, OpenAI-compatible)
  2. OpenRouter  (free models)
  3. Ollama      (local / offline)
  4. heuristic   (no network at all — always works)

Returns a dict: {"headline", "image_prompt", "provider", "notes"}.
"""

from __future__ import annotations

import json
import re

import requests

from config import Settings, get_settings

SYSTEM_PROMPT = (
    "You are a marketing copywriter and AI image-prompt engineer. "
    "Reply ONLY with a compact JSON object with exactly two keys: "
    '"headline" (short, punchy, max 8 words) and "image_prompt" '
    "(a detailed English text-to-image prompt describing subject, style, "
    "lighting, colors and composition)."
)


def _extract_json(text: str) -> dict:
    """Pull a JSON object out of a model reply that may be wrapped in prose."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return {}


def _normalise(data: dict, user_prompt: str, provider: str, notes: str = "") -> dict:
    headline = str(data.get("headline") or "").strip() or user_prompt.strip().title()[:60]
    image_prompt = str(data.get("image_prompt") or "").strip() or (
        f"{user_prompt}, professional marketing design, high detail, "
        "studio lighting, vibrant colors, 4k"
    )
    return {
        "headline": headline,
        "image_prompt": image_prompt,
        "provider": provider,
        "notes": notes,
    }


def _chat(base_url: str, api_key: str, model: str, user_prompt: str, timeout: float) -> dict:
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return _extract_json(content)


def _ollama(base_url: str, model: str, user_prompt: str, timeout: float) -> dict:
    resp = requests.post(
        f"{base_url.rstrip('/')}/api/chat",
        json={
            "model": model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    content = resp.json().get("message", {}).get("content", "")
    return _extract_json(content)


def generate_copy(user_prompt: str, settings: Settings | None = None) -> dict:
    """Produce a headline + image prompt for the given idea."""
    s = settings or get_settings()
    timeout = min(s.request_timeout, 120)

    if s.groq_api_key:
        try:
            data = _chat(s.groq_base_url, s.groq_api_key, s.groq_model, user_prompt, timeout)
            if data:
                return _normalise(data, user_prompt, "groq")
        except Exception as exc:
            note = f"Groq failed ({exc}); trying next provider."
        else:
            note = "Groq returned no usable JSON; trying next provider."
    else:
        note = "Groq not configured."

    if s.openrouter_api_key:
        try:
            data = _chat(
                s.openrouter_base_url,
                s.openrouter_api_key,
                s.openrouter_model,
                user_prompt,
                timeout,
            )
            if data:
                return _normalise(data, user_prompt, "openrouter", note)
        except Exception as exc:
            note += f" OpenRouter failed ({exc})."

    try:
        data = _ollama(s.ollama_base_url, s.ollama_model, user_prompt, timeout)
        if data:
            return _normalise(data, user_prompt, "ollama", note)
    except Exception as exc:
        note += f" Ollama failed ({exc})."

    return _normalise({}, user_prompt, "fallback", note + " Using local fallback copy.")


if __name__ == "__main__":  # pragma: no cover
    print(generate_copy("dashain sale poster for a Nepali clothing store"))
