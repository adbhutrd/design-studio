"""Canvas layer — poster composition and Penpot SVG export."""

from __future__ import annotations

import base64
import io
import re

from PIL import Image

from services import canvas


def test_compose_poster_adds_band(png_bytes):
    out = canvas.compose_poster(png_bytes, "Dashain Sale", "Up to 50% off")
    assert out.startswith(b"\x89PNG")
    # 1080 wide, image scaled proportionally, plus a 300 px band.
    expected_h = int(80 * (1080 / 120)) + 300
    assert Image.open(io.BytesIO(out)).size == (1080, expected_h)


def test_compose_poster_defaults_width_to_1080(png_bytes):
    out = canvas.compose_poster(png_bytes, "x")
    assert Image.open(io.BytesIO(out)).width == 1080


def test_compose_poster_handles_empty_headline(png_bytes):
    out = canvas.compose_poster(png_bytes, "")
    assert out.startswith(b"\x89PNG")


def test_svg_is_wellformed_and_embeds_image(png_bytes):
    svg = canvas.poster_svg(png_bytes, "Big Offer", "today only")
    assert svg.lstrip().startswith("<svg")
    assert svg.rstrip().endswith("</svg>")
    assert "Big Offer" in svg
    payload = re.search(r"base64,([A-Za-z0-9+/=]+)", svg).group(1)
    assert base64.b64decode(payload) == png_bytes


def test_svg_escapes_markup(png_bytes):
    svg = canvas.poster_svg(png_bytes, "Sale & <b>Deal</b>")
    assert "&amp;" in svg
    assert "&lt;b&gt;" in svg
    assert "<b>" not in svg


def test_wrap_respects_max_lines(png_bytes):
    img = Image.new("RGB", (400, 400))
    draw = canvas.ImageDraw.Draw(img)
    font = canvas._font(40)
    lines = canvas._wrap("a b c d e f g h i j" * 4, font, draw, 50, max_lines=2)
    assert len(lines) == 2
