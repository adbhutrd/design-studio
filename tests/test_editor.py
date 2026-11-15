"""Editing layer — pure Pillow, no network."""

from __future__ import annotations

import io

from PIL import Image

from services import editor


def _open(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def test_info_reports_dimensions(png_bytes):
    meta = editor.info(png_bytes)
    assert meta["width"] == 120
    assert meta["height"] == 80
    assert meta["format"] == "PNG"


def test_no_edits_returns_valid_png(png_bytes):
    out = editor.apply_edits(png_bytes)
    assert out.startswith(b"\x89PNG")
    assert _open(out).size == (120, 80)


def test_resize_width_keeps_aspect_ratio(png_bytes):
    out = editor.apply_edits(png_bytes, resize_width=240)
    assert _open(out).size == (240, 160)


def test_resize_width_has_a_floor(png_bytes):
    out = editor.apply_edits(png_bytes, resize_width=1)
    assert _open(out).width >= 16


def test_crop_uses_normalised_box(png_bytes):
    out = editor.apply_edits(png_bytes, crop=(0.0, 0.0, 0.5, 0.5))
    assert _open(out).size == (60, 40)


def test_grayscale_removes_colour(png_bytes):
    out = _open(editor.apply_edits(png_bytes, grayscale=True)).convert("RGB")
    r, g, b = out.getpixel((10, 10))
    assert r == g == b


def test_rotate_expands_canvas(png_bytes):
    out = editor.apply_edits(png_bytes, rotate=90)
    img = _open(out)
    assert img.size == (80, 120)


def test_rounded_corners_clears_corner_alpha(png_bytes):
    out = _open(editor.apply_edits(png_bytes, rounded_corners=24))
    assert out.mode == "RGBA"
    assert out.getpixel((0, 0))[3] == 0          # corner cut away
    assert out.getpixel((60, 40))[3] == 255      # centre intact


def test_brightness_increases_mean(png_bytes):
    from PIL import ImageStat

    base = ImageStat.Stat(_open(editor.apply_edits(png_bytes)).convert("L")).mean[0]
    bright = ImageStat.Stat(
        _open(editor.apply_edits(png_bytes, brightness=1.5)).convert("L")
    ).mean[0]
    assert bright > base


def test_flips_are_supported(png_bytes):
    out = _open(editor.apply_edits(png_bytes, flip_horizontal=True, flip_vertical=True))
    assert out.size == (120, 80)
