"""Storage naming and LLM reply parsing — no provider is contacted."""

from __future__ import annotations

import os
import re

from services import llm, storage


# ------------------------------------------------------------------ storage


def test_slug_strips_unsafe_characters():
    assert storage._slug("Dashain Sale / 50% off!") == "dashain-sale-50-off"


def test_slug_collapses_repeated_dashes():
    assert storage._slug("a   b") == "a-b"


def test_slug_falls_back_when_empty():
    assert storage._slug("!!!") == "design"


def test_slug_is_length_limited():
    assert len(storage._slug("x" * 200)) == 40


def test_save_output_writes_file(settings):
    path = storage.save_output(b"\x89PNG\r\n", "Dashain Sale", settings=settings)
    assert os.path.exists(path)
    assert os.path.basename(path).startswith("dashain-sale_")
    assert re.search(r"_\d{8}_\d{6}\.png$", path)
    assert open(path, "rb").read() == b"\x89PNG\r\n"


# ---------------------------------------------------------------------- llm


def test_extract_json_plain_object():
    assert llm._extract_json('{"headline": "Hi"}') == {"headline": "Hi"}


def test_extract_json_fenced_block():
    raw = '```json\n{"headline": "Hi", "image_prompt": "a cat"}\n```'
    assert llm._extract_json(raw)["image_prompt"] == "a cat"


def test_extract_json_from_prose():
    raw = 'Sure! Here you go:\n{"headline": "Hi"}\nHope that helps.'
    assert llm._extract_json(raw) == {"headline": "Hi"}


def test_extract_json_garbage_returns_empty():
    assert llm._extract_json("no json at all") == {}


def test_normalise_fills_missing_fields():
    out = llm._normalise({}, "dashain poster", "fallback")
    assert out["headline"]
    assert "dashain poster" in out["image_prompt"]
    assert out["provider"] == "fallback"


def test_normalise_keeps_model_output():
    out = llm._normalise(
        {"headline": "Big Sale", "image_prompt": "gold confetti"}, "x", "groq"
    )
    assert out == {
        "headline": "Big Sale",
        "image_prompt": "gold confetti",
        "provider": "groq",
        "notes": "",
    }
