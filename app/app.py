"""Open Design Studio — the Streamlit glue UI.

Two modes:
  * AI bata banaun   — idea lekha, free AI le image banchha.
  * Afno photo edit  — photo upload gara, edit + bg-remove + upscale + poster.

Run:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from config import get_settings
from pipeline import run_pipeline
from services import cleanup, editor

st.set_page_config(page_title="Open Design Studio", page_icon="🎨", layout="wide")

settings = get_settings()

st.title("🎨 Open Design Studio")
st.caption(
    "Zero-budget design ecosystem — Penpot + ComfyUI + Llama + rembg/Real-ESRGAN. "
    "Sabai free, browser bata."
)

MODE_GENERATE = "✨ AI bata banaun (generate)"
MODE_EDIT = "🖼️ Afno photo edit gara (upload)"

mode = st.radio("Mode", [MODE_GENERATE, MODE_EDIT], horizontal=True, label_visibility="collapsed")

uploaded = None
if mode == MODE_EDIT:
    uploaded = st.file_uploader(
        "Photo upload gara (PNG / JPG / WEBP) — phone ko photo pani chalchha",
        type=["png", "jpg", "jpeg", "webp"],
    )
    if uploaded is not None:
        try:
            meta = editor.info(uploaded.getvalue())
            st.caption(f"Uploaded: {meta['width']}×{meta['height']} px · {meta['format']}")
        except Exception as exc:
            st.warning(f"Image padhna sakiena: {exc}")

prompt = st.text_area(
    "Describe your design idea (Roman Nepali or English)",
    "Dashain sale poster for a Nepali clothing store, warm festive colors",
    height=90,
)

# --------------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("⚙️ Output")
    width = st.select_slider("Width", [512, 768, 1024, 1280, 1536], value=1024)
    height = st.select_slider("Height", [512, 768, 1024, 1280, 1536], value=1024)
    steps = st.slider("Sampling steps", 10, 50, 25, 5)
    make_poster = st.checkbox("Poster bana (headline sahit)", value=True)

    st.divider()
    st.header("🧽 Photo cleanup")
    do_bg_removal = st.checkbox("Remove background (rembg)", value=True)
    do_upscale = st.checkbox("Upscale x2 (Real-ESRGAN)", value=False)

    st.divider()
    st.header("🎛️ Photo edit")
    st.caption("Upload mode ma matra lagu hunchha.")
    brightness = st.slider("Brightness", 0.2, 2.0, 1.0, 0.05)
    contrast = st.slider("Contrast", 0.2, 2.0, 1.0, 0.05)
    saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.05)
    sharpness = st.slider("Sharpness", 0.0, 3.0, 1.0, 0.1)
    grayscale = st.checkbox("Black & white", value=False)
    rotation = st.slider("Rotate (°)", 0, 350, 0, 10)
    rounded = st.slider("Rounded corners (px)", 0, 300, 0, 10)
    resize_width = st.slider("Resize width (0 = rakhnu)", 0, 2048, 0, 32)
    square_crop = st.checkbox("Center square crop (poster ko lagi)", value=False)

    st.divider()
    st.caption("**Providers**")
    llm_provider = (
        "Groq"
        if settings.groq_api_key
        else "OpenRouter"
        if settings.openrouter_api_key
        else "fallback (no key)"
    )
    st.write(f"LLM: `{llm_provider}`")
    st.write(f"Image: `{settings.comfyui_gateway_url}`")
    st.write("Cleanup: " + ("`online`" if cleanup.health(settings) else "`offline (original kept)`"))

label = "🖼️ Apply edits" if mode == MODE_EDIT else "✨ Generate design"
go = st.button(label, type="primary", width="stretch")

if go:
    if mode == MODE_EDIT and uploaded is None:
        st.warning("Pehila photo upload garnus.")
    elif not prompt.strip() and mode == MODE_GENERATE:
        st.warning("Pehila idea lekhnus.")
    else:
        crop = None
        if mode == MODE_EDIT and square_crop:
            try:  # centre square crop as normalised (left, top, right, bottom)
                meta = editor.info(uploaded.getvalue())
                w, h = meta["width"], meta["height"]
                side = min(w, h)
                crop = (
                    (w - side) / 2 / w,
                    (h - side) / 2 / h,
                    (w + side) / 2 / w,
                    (h + side) / 2 / h,
                )
            except Exception:
                crop = None

        edit = (
            dict(
                brightness=brightness,
                contrast=contrast,
                saturation=saturation,
                sharpness=sharpness,
                grayscale=grayscale,
                rotate=rotation,
                rounded_corners=rounded,
                resize_width=(resize_width or None),
                crop=crop,
            )
            if mode == MODE_EDIT
            else None
        )

        progress = st.progress(0.0)
        status = st.empty()
        logs: list[str] = []

        def on_step(message: str) -> None:
            logs.append(message)
            progress.progress(min(1.0, len(logs) / 7))
            status.code("\n".join(logs[-4:]))

        with st.spinner("Running the free pipeline..."):
            result = run_pipeline(
                prompt,
                source_image=uploaded.getvalue() if uploaded is not None else None,
                edit=edit,
                width=width,
                height=height,
                steps=steps,
                do_bg_removal=do_bg_removal,
                do_upscale=do_upscale,
                make_poster=make_poster,
                settings=settings,
                on_step=on_step,
            )
        progress.progress(1.0)

        if result.final is None:
            st.error("Kei baniena. `.env` ma COMFYUI_GATEWAY_URL wa internet check garnus.")
        else:
            st.success(f"Banayo! Headline: **{result.headline}**  (copy via `{result.provider}`)")

            cols = st.columns(3)
            with cols[0]:
                st.subheader("1. Source")
                st.image(result.image, width="stretch")
                if result.image:
                    st.download_button("⬇️ PNG", result.image, "source.png", "image/png")
            with cols[1]:
                st.subheader("2. Edited / Cleaned")
                st.image(result.clean_image or result.image, width="stretch")
                if result.clean_image:
                    st.download_button("⬇️ PNG", result.clean_image, "edited.png", "image/png")
            with cols[2]:
                st.subheader("3. Poster" if make_poster else "3. Final")
                st.image(result.final, width="stretch")
                st.download_button("⬇️ PNG", result.final, "final.png", "image/png")

            if result.svg:
                st.download_button(
                    "⬇️ Import-ready SVG (Penpot)",
                    result.svg.encode("utf-8"),
                    "poster.svg",
                    "image/svg+xml",
                )
            if result.saved_path:
                st.caption(f"Saved to `{result.saved_path}`")

            with st.expander("Prompt + pipeline log"):
                st.write("**Image prompt**", result.image_prompt)
                st.code("\n".join(result.log))

st.divider()
st.caption(
    "Next: import the SVG into Penpot (https://design.penpot.app) for full layout editing, "
    "or trigger the same pipeline from n8n (see `../n8n/README.md`)."
)
