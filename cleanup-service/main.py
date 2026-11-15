"""Image cleanup microservice for the zero-budget design studio.

Endpoints
---------
GET  /health      -> {"status": "ok"}
POST /remove-bg   -> multipart field `file` -> PNG bytes with background removed
POST /upscale     -> multipart field `file`, query `scale` (default 2) -> PNG bytes

The service tries the best available engine for each task and always degrades
gracefully so the platform keeps working on a weak machine:

  background removal : rembg (u2net)  -> always required
  upscaling          : realesrgan-ncnn-vulkan binary (SR_BIN)
                       -> python realesrgan / basicsr package
                       -> Pillow LANCZOS resize (fallback, always works)
"""

from __future__ import annotations

import io
import os
import subprocess
import tempfile

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image

# ---------------------------------------------------------------- configuration

PORT = int(os.environ.get("PORT", "8000"))
REMBG_MODEL = os.environ.get("REMBG_MODEL", "u2net")
SR_BIN = os.environ.get("SR_BIN", "")  # path to realesrgan-ncnn-vulkan, optional

app = FastAPI(title="Design Studio Cleanup Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The rembg session is expensive to build, so keep one warm copy around.
_REMBG_SESSION = None
_REMBG_BACKEND = "new_session"


def _get_rembg_session():
    """Lazily create and cache a rembg inference session."""
    global _REMBG_SESSION, _REMBG_BACKEND
    if _REMBG_SESSION is not None:
        return _REMBG_SESSION
    try:
        from rembg import new_session  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on install
        raise RuntimeError(f"rembg is not installed: {exc}") from exc
    try:
        _REMBG_SESSION = new_session(REMBG_MODEL)
        _REMBG_BACKEND = "new_session"
    except Exception:
        # Older rembg versions expose the model name directly on remove().
        _REMBG_SESSION = REMBG_MODEL
        _REMBG_BACKEND = "model_name"
    return _REMBG_SESSION


async def _read_upload(file: UploadFile) -> bytes:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail={"error": "empty upload"})
    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail={"error": f"not a valid image: {exc}"}
        ) from exc
    return data


def _png_response(img: Image.Image) -> Response:
    buf = io.BytesIO()
    img.convert("RGBA").save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")


# ---------------------------------------------------------------------- health


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------- remove bg


def _remove_background(data: bytes) -> bytes:
    from rembg import remove  # type: ignore  # imported here so errors are clear

    session = _get_rembg_session()
    if _REMBG_BACKEND == "new_session":
        out = remove(data, session=session)
    else:
        out = remove(data, model_name=session)
    return out


@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)) -> Response:
    data = await _read_upload(file)
    try:
        result = _remove_background(data)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail={"error": f"background removal failed: {exc}"}
        ) from exc
    return Response(content=result, media_type="image/png")


# -------------------------------------------------------------------- upscale


def _upscale_with_binary(data: bytes, scale: int) -> bytes | None:
    """Run realesrgan-ncnn-vulkan if it is available on this machine."""
    if not SR_BIN or not os.path.exists(SR_BIN):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "in.png")
        dst = os.path.join(tmp, "out.png")
        with open(src, "wb") as fh:
            fh.write(data)
        cmd = [SR_BIN, "-i", src, "-o", dst, "-s", str(scale)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=600)
        except Exception:
            return None
        if not os.path.exists(dst):
            return None
        with open(dst, "rb") as fh:
            return fh.read()


def _upscale_with_python(data: bytes, scale: int) -> bytes | None:
    """Try the pip-installable realesrgan / basicsr stack."""
    try:
        import numpy as np  # type: ignore
        from basicsr.archs.rrdbnet_arch import RRDBNet  # type: ignore
        from realesrgan import RealESRGANer  # type: ignore
    except Exception:
        return None
    try:
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32)
        upsampler = RealESRGANer(scale=scale, model_path=None, model=model, tile=0, half=False)
        img = Image.open(io.BytesIO(data)).convert("RGB")
        out, _ = upsampler.enhance(np.array(img), outscale=scale)
        buf = io.BytesIO()
        Image.fromarray(out).save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return None


def _upscale_fallback(data: bytes, scale: int) -> bytes:
    """Always-works fallback: plain Lanczos resampling."""
    img = Image.open(io.BytesIO(data))
    new_size = (img.width * scale, img.height * scale)
    resized = img.resize(new_size, Image.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format="PNG")
    return buf.getvalue()


@app.post("/upscale")
async def upscale(file: UploadFile = File(...), scale: int = Query(2, ge=1, le=8)) -> Response:
    data = await _read_upload(file)
    try:
        for engine in (_upscale_with_binary, _upscale_with_python):
            result = engine(data, scale)
            if result:
                return Response(content=result, media_type="image/png")
        return Response(content=_upscale_fallback(data, scale), media_type="image/png")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail={"error": f"upscale failed: {exc}"}
        ) from exc


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
