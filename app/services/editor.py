"""Editing layer — edits an uploaded photo with Pillow only (no GPU, no network).

Every option is optional and defaults to "leave it alone", so the caller can pass
just the sliders the user touched. Phone photos are auto-rotated using their EXIF
orientation before anything else.
"""

from __future__ import annotations

import io

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageOps


def _to_rgba(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img)  # honour phone camera orientation
    return img.convert("RGBA")


def apply_edits(
    data: bytes,
    *,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    sharpness: float = 1.0,
    grayscale: bool = False,
    rotate: int = 0,
    crop: tuple[float, float, float, float] | None = None,
    resize_width: int | None = None,
    rounded_corners: int = 0,
    flip_horizontal: bool = False,
    flip_vertical: bool = False,
) -> bytes:
    """Apply the requested edits and return PNG bytes.

    `crop` is normalised (left, top, right, bottom) in 0..1.
    `rotate` is clockwise degrees. `resize_width` keeps the aspect ratio.
    """
    img = _to_rgba(data)

    if crop:
        l, t, r, b = crop
        w, h = img.size
        box = (int(l * w), int(t * h), int(r * w), int(b * h))
        if box[2] > box[0] and box[3] > box[1]:
            img = img.crop(box)

    if flip_horizontal:
        img = ImageOps.mirror(img)
    if flip_vertical:
        img = ImageOps.flip(img)

    if rotate:
        # PIL rotates counter-clockwise, so negate for a clockwise slider.
        img = img.rotate(-int(rotate) % 360, expand=True, resample=Image.BICUBIC)

    if resize_width:
        new_w = max(16, int(resize_width))
        new_h = max(16, int(round(img.height * new_w / img.width)))
        img = img.resize((new_w, new_h), Image.LANCZOS)

    if grayscale:
        img = ImageOps.grayscale(img).convert("RGBA")

    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    if sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)

    if rounded_corners and rounded_corners > 0:
        radius = int(rounded_corners)
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, img.size[0] - 1, img.size[1] - 1], radius=radius, fill=255
        )
        # multiply with any existing alpha so we never re-add what was removed
        combined = ImageChops.multiply(img.getchannel("A"), mask)
        img.putalpha(combined)

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def info(data: bytes) -> dict:
    """Small helper for the UI: basic facts about an uploaded image."""
    img = Image.open(io.BytesIO(data))
    return {"width": img.width, "height": img.height, "mode": img.mode, "format": img.format}
