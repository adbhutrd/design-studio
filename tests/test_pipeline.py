"""Pipeline glue. Every network provider is stubbed, so this runs offline."""

from __future__ import annotations

import io

from PIL import Image

import pipeline
from services import cleanup, llm


def _stub_llm(monkeypatch):
    monkeypatch.setattr(
        llm,
        "generate_copy",
        lambda prompt, settings=None: {
            "headline": "Dashain Sale",
            "image_prompt": "festive poster, warm colours",
            "provider": "stub",
            "notes": "",
        },
    )


def _stub_cleanup(monkeypatch, keep=True):
    monkeypatch.setattr(
        cleanup, "remove_background", lambda data, settings=None: (data, "stubbed")
    )
    monkeypatch.setattr(cleanup, "upscale", lambda data, scale=2, settings=None: (data, "stubbed"))


def test_source_image_with_poster_saves_output(monkeypatch, png_bytes, settings):
    _stub_llm(monkeypatch)
    _stub_cleanup(monkeypatch)

    result = pipeline.run_pipeline(
        "profile poster bana",
        source_image=png_bytes,
        do_bg_removal=True,
        make_poster=True,
        settings=settings,
    )

    assert result.headline == "Dashain Sale"
    assert result.image == png_bytes
    assert result.clean_image is not None
    assert result.poster is not None
    assert result.svg.startswith("<svg")
    assert result.final == result.poster
    assert result.saved_path.endswith(".png")
    assert result.provider == "stub"
    assert any("2/5" in line for line in result.log)
    assert any("5/5" in line for line in result.log)


def test_edits_are_applied_to_uploaded_photo(monkeypatch, png_bytes, settings):
    _stub_llm(monkeypatch)
    _stub_cleanup(monkeypatch)

    result = pipeline.run_pipeline(
        "edit",
        source_image=png_bytes,
        edit={"resize_width": 240},
        make_poster=False,
        settings=settings,
    )

    assert Image.open(io.BytesIO(result.edited)).size == (240, 160)
    assert result.poster is None
    assert result.final == result.clean_image


def test_failed_edit_keeps_original(monkeypatch, png_bytes, settings):
    _stub_llm(monkeypatch)
    _stub_cleanup(monkeypatch)

    def boom(*_args, **_kwargs):
        raise ValueError("bad crop")

    from services import editor

    monkeypatch.setattr(editor, "apply_edits", boom)

    result = pipeline.run_pipeline(
        "edit", source_image=png_bytes, edit={"crop": (0, 0, 0, 0)},
        make_poster=False, settings=settings,
    )

    assert result.edited is None
    assert any("edit failed" in line for line in result.log)


def test_generation_stops_when_no_image_provider(monkeypatch, settings):
    _stub_llm(monkeypatch)
    from services import imagegen

    monkeypatch.setattr(
        imagegen, "generate_image", lambda *a, **k: (None, "none", "all providers down")
    )

    result = pipeline.run_pipeline("a poster", settings=settings)

    assert result.image is None
    assert result.final is None
    assert result.saved_path is None
    assert any("no image generated" in line for line in result.log)


def test_generation_happy_path(monkeypatch, png_bytes, settings):
    _stub_llm(monkeypatch)
    _stub_cleanup(monkeypatch)
    from services import imagegen

    monkeypatch.setattr(
        imagegen, "generate_image", lambda *a, **k: (png_bytes, "pollinations", "note")
    )

    result = pipeline.run_pipeline("a poster", settings=settings)

    assert result.image == png_bytes
    assert result.saved_path
    assert result.poster is not None


def test_on_step_callback_receives_progress(monkeypatch, png_bytes, settings):
    _stub_llm(monkeypatch)
    _stub_cleanup(monkeypatch)
    seen: list[str] = []

    pipeline.run_pipeline(
        "x", source_image=png_bytes, settings=settings, on_step=seen.append
    )

    assert seen
    assert seen == pipeline.run_pipeline(
        "x", source_image=png_bytes, settings=settings
    ).log
