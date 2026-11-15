"""ComfyUI gateway — graph construction and history parsing (no ComfyUI needed)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="gateway tests need FastAPI installed")

MODULE_PATH = Path(__file__).resolve().parents[1] / "comfyui-gateway" / "main.py"


def _load():
    spec = importlib.util.spec_from_file_location("gateway_main", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gateway = _load()


def test_graph_has_all_stable_diffusion_nodes():
    req = gateway.GenerateRequest(prompt="a red lantern")
    graph = gateway._build_graph(req)

    assert graph["3"]["class_type"] == "KSampler"
    assert graph["4"]["inputs"]["ckpt_name"] == gateway.COMFYUI_CKPT
    assert graph["5"]["inputs"] == {"width": 1024, "height": 1024, "batch_size": 1}
    assert graph["6"]["inputs"]["text"] == "a red lantern"
    assert graph["9"]["class_type"] == "SaveImage"


def test_graph_seed_is_random_when_unset():
    req = gateway.GenerateRequest(prompt="x")
    a = gateway._build_graph(req)["3"]["inputs"]["seed"]
    b = gateway._build_graph(req)["3"]["inputs"]["seed"]
    assert a != b


def test_graph_honours_explicit_seed_and_size():
    req = gateway.GenerateRequest(prompt="x", seed=42, width=768, height=512, steps=12)
    graph = gateway._build_graph(req)
    assert graph["3"]["inputs"]["seed"] == 42
    assert graph["3"]["inputs"]["steps"] == 12
    assert graph["5"]["inputs"]["width"] == 768


def test_request_rejects_empty_prompt():
    with pytest.raises(Exception):
        gateway.GenerateRequest(prompt="")


def test_request_rejects_out_of_range_size():
    with pytest.raises(Exception):
        gateway.GenerateRequest(prompt="x", width=4096)


def test_first_image_picks_filename():
    entry = {
        "outputs": {
            "9": {"images": [{"filename": "designstudio_00001_.png", "subfolder": "", "type": "output"}]}
        }
    }
    assert gateway._first_image(entry)["filename"] == "designstudio_00001_.png"


def test_first_image_returns_none_when_empty():
    assert gateway._first_image({"outputs": {}}) is None
