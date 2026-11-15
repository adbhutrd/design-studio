"""Image cleanup layer — background removal and upscaling.

Talks to the `cleanup-service` (rembg + Real-ESRGAN). If that service is not
running, the original image is returned unchanged with a note, so the pipeline
never hard-fails on a weak machine.
"""

from __future__ import annotations

import requests

from config import Settings, get_settings


def _post_image(path: str, data: bytes, params: dict | None, s: Settings) -> bytes | None:
    resp = requests.post(
        f"{s.cleanup_url}{path}",
        files={"file": ("image.png", data, "image/png")},
        params=params or {},
        timeout=s.request_timeout,
    )
    resp.raise_for_status()
    if resp.content and resp.headers.get("content-type", "").startswith("image/"):
        return resp.content
    return None


def remove_background(data: bytes, settings: Settings | None = None) -> tuple[bytes, str]:
    """Return (png_bytes, note). Falls back to the original on failure."""
    s = settings or get_settings()
    try:
        out = _post_image("/remove-bg", data, None, s)
        if out:
            return out, "background removed (rembg)"
        return data, "cleanup-service returned no image; kept original."
    except Exception as exc:
        return data, f"cleanup-service unavailable ({exc}); kept original."


def upscale(
    data: bytes, scale: int = 2, settings: Settings | None = None
) -> tuple[bytes, str]:
    """Return (png_bytes, note). Falls back to the original on failure."""
    s = settings or get_settings()
    try:
        out = _post_image("/upscale", data, {"scale": scale}, s)
        if out:
            return out, f"upscaled x{scale} (Real-ESRGAN)"
        return data, "cleanup-service returned no image; kept original."
    except Exception as exc:
        return data, f"cleanup-service unavailable ({exc}); kept original."


def health(settings: Settings | None = None) -> bool:
    s = settings or get_settings()
    try:
        return requests.get(f"{s.cleanup_url}/health", timeout=5).json().get("status") == "ok"
    except Exception:
        return False
