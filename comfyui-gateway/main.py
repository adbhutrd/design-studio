"""ComfyUI synchronous gateway.

Stock ComfyUI is asynchronous: ``POST /prompt`` returns only a ``prompt_id`` and
the PNG is later written to ComfyUI's ``output/`` folder. Both the Streamlit app
and the n8n workflow need a single call that returns the finished image, so this
tiny service owns that logic exactly once:

    POST /generate  -> submit graph -> poll /history/{id} -> fetch /view -> PNG

It is intentionally dependency-light (FastAPI + requests) so it can run on the
weakest machine, next to the free Colab tunnel.
"""

from __future__ import annotations

import os
import time
import uuid

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
COMFYUI_CKPT = os.environ.get("COMFYUI_CKPT", "sd_xl_base_1.0.safetensors")
POLL_INTERVAL = float(os.environ.get("COMFYUI_POLL_INTERVAL", "2"))
TIMEOUT = float(os.environ.get("COMFYUI_TIMEOUT", "300"))

app = FastAPI(title="ComfyUI Gateway", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    negative_prompt: str = "blurry, low quality, watermark, text, deformed"
    width: int = Field(1024, ge=256, le=2048)
    height: int = Field(1024, ge=256, le=2048)
    steps: int = Field(25, ge=1, le=100)
    cfg: float = Field(7.0, ge=1, le=20)
    seed: int | None = None
    ckpt: str | None = None


def _build_graph(req: GenerateRequest) -> dict:
    """Minimal SDXL text2img graph in ComfyUI API format."""
    seed = req.seed if req.seed is not None else uuid.uuid4().int % (2**32)
    ckpt = req.ckpt or COMFYUI_CKPT
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": req.steps,
                "cfg": req.cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": ckpt},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": req.width, "height": req.height, "batch_size": 1},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": req.prompt, "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": req.negative_prompt, "clip": ["4", 1]},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "designstudio", "images": ["8", 0]},
        },
    }


def _first_image(history_entry: dict) -> dict | None:
    """Pull the first ``{filename, subfolder, type}`` out of a history entry."""
    for node_output in (history_entry.get("outputs") or {}).values():
        for img in node_output.get("images", []):
            if img.get("filename"):
                return img
    return None


@app.get("/health")
def health() -> dict:
    """Report whether the upstream ComfyUI instance is reachable."""
    try:
        r = requests.get(f"{COMFYUI_URL}/system_stats", timeout=10)
        r.raise_for_status()
        return {"status": "ok", "comfyui": "reachable"}
    except Exception as exc:  # pragma: no cover - network dependent
        return {"status": "degraded", "comfyui": str(exc)}


@app.post("/generate")
def generate(req: GenerateRequest) -> Response:
    """Submit a text2img job and block until the finished PNG is available."""
    try:
        submit = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": _build_graph(req)},
            timeout=30,
        )
        submit.raise_for_status()
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail={"error": f"ComfyUI submit failed: {exc}"}
        ) from exc

    prompt_id = submit.json().get("prompt_id")
    if not prompt_id:
        raise HTTPException(status_code=502, detail={"error": "no prompt_id returned"})

    deadline = time.time() + TIMEOUT
    image_info = None
    while time.time() < deadline:
        try:
            hist = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=15)
            hist.raise_for_status()
            entry = hist.json().get(prompt_id)
            if entry:
                image_info = _first_image(entry)
                if image_info:
                    break
        except Exception:
            # transient; keep polling until the deadline
            pass
        time.sleep(POLL_INTERVAL)

    if not image_info:
        raise HTTPException(
            status_code=504,
            detail={"error": f"timed out waiting for ComfyUI after {TIMEOUT:.0f}s"},
        )

    try:
        view = requests.get(
            f"{COMFYUI_URL}/view",
            params={
                "filename": image_info["filename"],
                "subfolder": image_info.get("subfolder", ""),
                "type": image_info.get("type", "output"),
            },
            timeout=60,
        )
        view.raise_for_status()
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail={"error": f"ComfyUI fetch failed: {exc}"}
        ) from exc

    return Response(content=view.content, media_type="image/png")


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8100")),
    )
