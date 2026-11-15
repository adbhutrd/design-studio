"""The pipeline — this is the "glue" the whole project is about.

Two ways in:
  * text only          -> idea -> Llama -> image generation -> ...
  * uploaded photo     -> your photo -> edits -> background removal -> upscale -> ...

    -> canvas (poster) -> storage (saved)

Every step degrades gracefully: a missing provider is recorded in `log` instead
of aborting the run, so a weak laptop with only some free tiers configured still
produces a design.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from config import Settings, get_settings
from services import canvas, cleanup, editor, imagegen, llm, storage

Step = Callable[[str], None]


@dataclass
class PipelineResult:
    headline: str = ""
    image_prompt: str = ""
    provider: str = ""
    image: bytes | None = None          # generated image or the uploaded photo
    edited: bytes | None = None         # after editor.apply_edits (uploads only)
    clean_image: bytes | None = None    # after background removal / upscale
    poster: bytes | None = None
    svg: str | None = None
    final: bytes | None = None          # poster if made, else the cleaned image
    saved_path: str | None = None
    log: list[str] = field(default_factory=list)


def run_pipeline(
    user_prompt: str,
    *,
    source_image: bytes | None = None,
    edit: dict | None = None,
    width: int = 1024,
    height: int = 1024,
    steps: int = 25,
    do_bg_removal: bool = True,
    do_upscale: bool = False,
    scale: int = 2,
    make_poster: bool = True,
    settings: Settings | None = None,
    on_step: Step | None = None,
) -> PipelineResult:
    """Run the design flow (generation or upload-editing) and return everything."""
    s = settings or get_settings()
    result = PipelineResult()

    def step(message: str) -> None:
        result.log.append(message)
        if on_step:
            on_step(message)

    step("1/5 Writing headline + image prompt with Llama...")
    copy = llm.generate_copy(user_prompt or "photo edit", s)
    result.headline = copy["headline"]
    result.image_prompt = copy["image_prompt"]
    result.provider = copy["provider"]
    step(f"     copy via {copy['provider']}: {result.headline!r}")

    if source_image is not None:
        step("2/5 Using your uploaded photo...")
        result.image = source_image
        working = source_image
        if edit:
            step("     applying photo edits (Pillow)...")
            try:
                working = editor.apply_edits(working, **edit)
                result.edited = working
                step("     edits applied")
            except Exception as exc:
                step(f"     edit failed ({exc}); kept original")
        else:
            step("     no edits requested")
    else:
        step("2/5 Generating image (ComfyUI, then Pollinations fallback)...")
        image, provider, note = imagegen.generate_image(
            result.image_prompt, width=width, height=height, steps=steps, settings=s
        )
        if note:
            step(f"     {note}")
        if image is None:
            step("     no image generated — stopping before the canvas step.")
            return result
        result.image = image
        working = image
        step(f"     image ready via {provider}")

    if do_bg_removal:
        step("3/5 Removing background (rembg)...")
        working, note = cleanup.remove_background(working, s)
        step(f"     {note}")
    else:
        step("3/5 Background removal skipped.")
    result.clean_image = working

    if do_upscale:
        step(f"4/5 Upscaling x{scale} (Real-ESRGAN)...")
        working, note = cleanup.upscale(working, scale, s)
        step(f"     {note}")
        result.clean_image = working
    else:
        step("4/5 Upscale skipped.")

    if make_poster:
        step("5/5 Composing poster + Penpot SVG...")
        result.poster = canvas.compose_poster(working, result.headline)
        result.svg = canvas.poster_svg(working, result.headline, (user_prompt or "")[:80])
        result.final = result.poster
    else:
        step("5/5 Poster skipped — returning the edited photo.")
        result.final = working

    if result.final is not None:
        result.saved_path = storage.save_output(result.final, result.headline, settings=s)
        step(f"     saved -> {result.saved_path}")

    return result


if __name__ == "__main__":  # pragma: no cover
    out = run_pipeline(
        "Dashain sale poster for a Nepali clothing store",
        do_bg_removal=False,
        on_step=print,
    )
    print("headline:", out.headline)
    print("saved:", out.saved_path)
