"""Storage layer — saves finished designs.

Kept deliberately simple and offline: files land in `OUTPUT_DIR`. Point that at a
synced folder, or swap this module for Supabase / Cloudflare R2 later — the rest
of the pipeline only needs `save_output()`.
"""

from __future__ import annotations

import os
from datetime import datetime

from config import Settings, get_settings

_SAFE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")


def _slug(text: str, max_len: int = 40) -> str:
    cleaned = "".join(c if c in _SAFE else "-" for c in text.lower()).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return (cleaned or "design")[:max_len]


def save_output(
    data: bytes,
    prefix: str,
    ext: str = "png",
    settings: Settings | None = None,
) -> str:
    """Write bytes to the output directory and return the full path."""
    s = settings or get_settings()
    os.makedirs(s.output_dir, exist_ok=True)
    name = f"{_slug(prefix)}_{datetime.now():%Y%m%d_%H%M%S}.{ext}"
    path = os.path.join(s.output_dir, name)
    with open(path, "wb") as fh:
        fh.write(data)
    return path
