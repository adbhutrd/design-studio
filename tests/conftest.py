"""Shared fixtures. Keeps the suite offline: no network, no GPU, no API keys."""

from __future__ import annotations

import io
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


@pytest.fixture
def png_bytes() -> bytes:
    """A small opaque RGB PNG, generated in-memory."""
    img = Image.new("RGB", (120, 80), (200, 60, 30))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def settings(tmp_path):
    """Real settings with the output directory redirected into tmp_path."""
    from config import get_settings

    return replace(get_settings(), output_dir=str(tmp_path / "outputs"))
