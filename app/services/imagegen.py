"""Image generation layer — free HD images with no GPU on your own machine.

Primary : ComfyUI through the synchronous gateway (free Colab GPU).
Fallback: Pollinations.ai (free public text-to-image API, no key).

Returns (png_bytes, provider_name).
"""

from __future__ import annotations

import urllib.parse

import requests

from config import Settings, get_settings


def _via_gateway(
    prompt: str, width: int, height: int, steps: int, s: Settings
) -> bytes | None:
    resp = requests.post(
        f"{s.comfyui_gateway_url}/generate",
        json={
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
        },
        timeout=s.request_timeout,
    )
    resp.raise_for_status()
    if resp.content and resp.headers.get("content-type", "").startswith("image/"):
        return resp.content
    return None


def _via_pollinations(prompt: str, width: int, height: int, s: Settings) -> bytes | None:
    url = f"{s.pollinations_url}/{urllib.parse.quote(prompt)}"
    resp = requests.get(
        url,
        params={"width": width, "height": height, "nologo": "true"},
        timeout=s.request_timeout,
    )
    resp.raise_for_status()
    if resp.content and resp.headers.get("content-type", "").startswith("image/"):
        return resp.content
    return None


def generate_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    steps: int = 25,
    settings: Settings | None = None,
) -> tuple[bytes | None, str, str]:
    """Generate an image. Returns (bytes|None, provider, note)."""
    s = settings or get_settings()
    note = ""

    try:
        data = _via_gateway(prompt, width, height, steps, s)
        if data:
            return data, "comfyui", note
        note = "ComfyUI gateway returned no image."
    except Exception as exc:
        note = f"ComfyUI gateway unavailable ({exc})."

    try:
        data = _via_pollinations(prompt, width, height, s)
        if data:
            return data, "pollinations", note + " Used Pollinations.ai fallback."
    except Exception as exc:
        note += f" Pollinations failed ({exc})."

    return None, "none", note + " No image provider worked."
