"""Canvas layer — compose a marketing poster and export a Penpot-ready SVG.

The heavy layout work happens in Penpot (free, open-source). This module builds a
good-enough first draft automatically (image + headline + accent band) so the user
gets a finished poster immediately, plus an `.svg` that imports straight into
Penpot for fine-tuning.
"""

from __future__ import annotations

import base64
import io
import os

from PIL import Image, ImageDraw, ImageFont

# Accent colour of the headline band (amber) and page background.
BAND_COLOR = (245, 158, 11, 255)
BG_COLOR = (17, 17, 27, 255)
HEADLINE_COLOR = (17, 17, 27)
SUBTITLE_COLOR = (70, 45, 0)

_FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    try:  # Pillow >= 10.1 can scale the built-in bitmap font
        return ImageFont.load_default(size=size)
    except Exception:  # pragma: no cover - very old Pillow
        return ImageFont.load_default()


def _wrap(text: str, font, draw: ImageDraw.ImageDraw, max_width: int, max_lines: int = 2) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines[:max_lines]


def compose_poster(
    image_bytes: bytes,
    headline: str,
    subtitle: str = "",
    width: int = 1080,
    band_height: int = 300,
) -> bytes:
    """Paste the generated image above a solid headline band and return PNG."""
    base = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    ratio = width / base.width
    img = base.resize((width, max(1, int(base.height * ratio))), Image.LANCZOS)

    canvas = Image.new("RGBA", (width, img.height + band_height), BG_COLOR)
    canvas.paste(img, (0, 0), img)

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, img.height, width, img.height + band_height], fill=BAND_COLOR)

    margin = int(width * 0.05)
    headline_font = _font(int(width * 0.062))
    subtitle_font = _font(int(width * 0.032))

    y = img.height + int(band_height * 0.14)
    for line in _wrap(headline, headline_font, draw, width - 2 * margin, max_lines=2):
        draw.text((margin, y), line, font=headline_font, fill=HEADLINE_COLOR)
        y += int(width * 0.072)

    if subtitle:
        draw.text((margin, y + int(band_height * 0.02)), subtitle[:90], font=subtitle_font, fill=SUBTITLE_COLOR)

    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="PNG")
    return out.getvalue()


def poster_svg(image_bytes: bytes, headline: str, subtitle: str = "", width: int = 1080) -> str:
    """Return an SVG of the poster that can be imported into Penpot."""
    base = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    ratio = width / base.width
    img_h = max(1, int(base.height * ratio))
    band = 300
    total_h = img_h + band
    b64 = base64.b64encode(image_bytes).decode("ascii")

    safe_headline = (headline or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_subtitle = (subtitle or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{total_h}" viewBox="0 0 {width} {total_h}">
  <rect width="{width}" height="{total_h}" fill="#11111b"/>
  <image x="0" y="0" width="{width}" height="{img_h}" preserveAspectRatio="xMidYMid slice"
         xlink:href="data:image/png;base64,{b64}"/>
  <rect x="0" y="{img_h}" width="{width}" height="{band}" fill="#f59e0b"/>
  <text x="{int(width * 0.05)}" y="{img_h + int(band * 0.42)}" font-family="sans-serif"
        font-size="{int(width * 0.062)}" font-weight="bold" fill="#11111b">{safe_headline}</text>
  <text x="{int(width * 0.05)}" y="{img_h + int(band * 0.78)}" font-family="sans-serif"
        font-size="{int(width * 0.032)}" fill="#462d00">{safe_subtitle}</text>
</svg>
"""
