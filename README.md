# Open Design Studio

A zero-budget design platform: generate a marketing poster from a sentence, or
edit one of your own photos — with no subscriptions, no GPU on your own machine,
and no paid API required.

Every layer is an independent, replaceable service, and the *glue* that joins
them is the actual product:

```
idea (text)                    your photo (PNG/JPG/WEBP)
     │                                  │
     ▼                                  ▼
  Llama ─ writes headline +        Pillow ─ tone, crop, rotate,
  image prompt                      rounded corners, B&W
     │                                  │
     ▼                                  │
  ComfyUI (free Colab GPU)             │
  └─ Pollinations.ai fallback          │
     │                                  │
     └──────────────┬───────────────────┘
                    ▼
              rembg — background removal
                    ▼
           Real-ESRGAN — 2× HD upscale
                    ▼
      canvas — poster compose + Penpot-ready SVG
                    ▼
         storage — saved to local disk
```

A missing provider never breaks a run: each step records what it did in the
pipeline log and the flow continues with the next free option.

---

## Table of contents

- [What it does](#what-it-does)
- [Architecture](#architecture)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Service reference](#service-reference)
- [Running as a service](#running-as-a-service)
- [Docker](#docker)
- [Development](#development)
- [Limitations](#limitations)
- [License](#license)

---

## What it does

| Capability | Engine | Cost |
|---|---|---|
| Marketing copy + image prompt | Llama via Groq / OpenRouter / Ollama | free tier |
| Image generation | ComfyUI on a free Colab GPU, Pollinations.ai fallback | free |
| Background removal | `rembg` (u2net) | free, local |
| HD upscaling | Real-ESRGAN (binary → Python → Lanczos fallback) | free, local |
| Poster composition | Pillow + SVG export for Penpot | free, local |
| Photo editing | Pillow: exposure, contrast, saturation, sharpness, crop, rotate, rounded corners | free, local |
| Orchestration | n8n workflow (headless HTTP) | self-hosted, free |

The result is a finished PNG plus an `.svg` that imports straight into
[Penpot](https://penpot.app) for pixel-level layout work.

---

## Architecture

```
┌──────────────┐   :8501   ┌──────────────┐
│  Streamlit   │──────────▶│  pipeline.py │
│   app/       │           │  (the glue)  │
└──────────────┘           └──────┬───────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌───────────────┐        ┌────────────────┐        ┌────────────────┐
│ services/llm  │        │ services/      │        │ services/      │
│ Groq→OpenRtr→ │        │ imagegen       │        │ cleanup        │
│ Ollama→local  │        │ gateway→Poll.  │        │ rembg + ESRGAN │
└───────────────┘        └───────┬────────┘        └───────┬────────┘
                                 ▼                         ▼
                     ┌────────────────────┐    ┌────────────────────┐
                     │ comfyui-gateway    │    │ cleanup-service    │
                     │ :8100 (sync API)   │    │ :8000 (FastAPI)    │
                     └─────────┬──────────┘    └────────────────────┘
                               ▼
                     ComfyUI on free Colab GPU
                     (notebooks/comfyui_colab.ipynb)
```

Why two side services instead of one monolith:

- **`comfyui-gateway`** turns ComfyUI's *asynchronous* API (`POST /prompt` →
  `prompt_id` → poll `/history` → `GET /view`) into one blocking call that
  returns the finished PNG. Both the Streamlit app and n8n use it, so the
  polling logic exists exactly once.
- **`cleanup-service`** holds the expensive ML imports (`rembg`, ONNX runtime)
  in one warm process, so the UI never pays a model-load cost.

---

## Quick start

Requirements: Python 3.11+, ~2 GB free disk (rembg model), Linux/macOS.

```bash
git clone <your-fork-url> design-studio
cd design-studio

bash setup.sh                 # venv + deps + .env from template
$EDITOR .env                  # optional: add GROQ_API_KEY (free)
bash start-all.sh             # cleanup :8000, gateway :8100, app :8501
```

Open **http://127.0.0.1:8501**.

Without any API key the platform still works: copy falls back to a local
heuristic and images fall back to Pollinations.ai.

Manage the stack:

```bash
bash start-all.sh          # start (stops an old instance first)
bash start-all.sh status   # health of all three services
bash start-all.sh restart
bash start-all.sh stop
```

Prefer separate terminals?

```bash
source .venv/bin/activate
python cleanup-service/main.py                            # :8000
COMFYUI_URL=<colab-tunnel-url> python comfyui-gateway/main.py   # :8100
streamlit run app/app.py                                  # :8501
```

To get real SDXL-quality images, open `notebooks/comfyui_colab.ipynb` in Google
Colab, run it, and put the Cloudflare tunnel URL into `COMFYUI_URL` in `.env`.

---

## Configuration

All configuration is environment-driven; see [`.env.example`](.env.example) for
the annotated template. Nothing is mandatory — an empty value disables that
provider and the next fallback takes over.

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | *(empty)* | Llama copywriting (recommended, fastest free tier) |
| `OPENROUTER_API_KEY` | *(empty)* | Second LLM option, free models |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Fully offline LLM option |
| `COMFYUI_GATEWAY_URL` | `http://127.0.0.1:8100` | Synchronous image-generation gateway |
| `COMFYUI_URL` | `http://127.0.0.1:8188` | ComfyUI instance (Colab tunnel) |
| `COMFYUI_CKPT` | `sd_xl_base_1.0.safetensors` | Checkpoint name inside ComfyUI |
| `POLLINATIONS_URL` | `https://image.pollinations.ai/prompt` | Keyless image fallback |
| `CLEANUP_URL` | `http://127.0.0.1:8000` | Background removal + upscale service |
| `REMBG_MODEL` | `u2net` | Segmentation model |
| `SR_BIN` | *(empty)* | Path to `realesrgan-ncnn-vulkan` for true HD |
| `OUTPUT_DIR` | `./app/outputs` | Where finished designs are written |
| `REQUEST_TIMEOUT` | `600` | Per-request timeout in seconds |

> **Never commit `.env`.** It is git-ignored, and `SECURITY.md` explains how to
> rotate a key if one is ever exposed.

---

## Service reference

### `cleanup-service` — port 8000

| Method | Path | Body / query | Returns |
|---|---|---|---|
| `GET` | `/health` | — | `{"status": "ok"}` |
| `POST` | `/remove-bg` | multipart `file` | PNG with transparent background |
| `POST` | `/upscale` | multipart `file`, `?scale=1..8` | PNG at `scale×` |

Upscaling tries `realesrgan-ncnn-vulkan` (if `SR_BIN` is set), then the Python
`realesrgan` package, then Pillow Lanczos. It never returns an error for a
missing engine.

### `comfyui-gateway` — port 8100

| Method | Path | Body | Returns |
|---|---|---|---|
| `GET` | `/health` | — | `{"status": "ok"\|"degraded", "comfyui": ...}` |
| `POST` | `/generate` | `{prompt, negative_prompt, width, height, steps, cfg, seed, ckpt}` | `image/png` |

Submits a minimal SDXL text2img graph, polls ComfyUI, and streams the finished
image back. Returns `502` when ComfyUI is unreachable and `504` on timeout
(`COMFYUI_TIMEOUT`, default 300 s).

### `app` — port 8501

Streamlit UI with two modes: **generate** (text → poster) and **upload** (photo
→ edit → clean → poster). The sidebar exposes output size, sampling steps,
cleanup toggles, and the full edit stack. Every run shows the headline, the
image prompt, and the step-by-step pipeline log.

CLI use of the same pipeline:

```bash
PYTHONPATH=app .venv/bin/python - <<'PY'
import pipeline
photo = open("my-photo.jpg", "rb").read()
result = pipeline.run_pipeline(
    "make a profile poster",
    source_image=photo,
    edit={"brightness": 1.2, "rounded_corners": 20, "resize_width": 800},
    do_bg_removal=True,
    make_poster=True,
    on_step=print,
)
print(result.saved_path)
PY
```

---

## Running as a service

For an always-on install on a Linux box (systemd *user* units, survives logout
with lingering enabled):

```bash
bash deploy/install-service.sh
systemctl --user status design-studio
journalctl --user -u design-studio -f
bash deploy/install-service.sh --uninstall    # remove
```

- `design-studio.service` runs `deploy/run-stack.sh`, which supervises the three
  children and exits if *any* of them dies; `Restart=always` then brings the
  whole stack back.
- `design-studio-health.timer` probes all three health endpoints every two
  minutes and restarts the service if one stops answering — this catches a
  wedged supervisor that still looks "running" to systemd.

Run either the manual script **or** the service, never both: they contend for
the same ports. The installer stops a manual instance automatically.

---

## Docker

```bash
cp .env.example .env
docker compose up -d          # app :8501, n8n :5678, cleanup :8000, gateway :8100
```

Penpot is deliberately not bundled — its official compose is a five-service
stack (frontend, backend, exporter, Postgres, Redis, MinIO). Use Penpot Cloud
for free, or their own compose file.

The n8n workflow in [`n8n/workflows/design-pipeline.json`](n8n/workflows/design-pipeline.json)
runs the same pipeline headlessly: import it, then `POST /webhook/design`.

---

## Development

```bash
make setup     # venv + runtime + dev dependencies
make test      # pytest
make lint      # ruff (pyflakes rules)
make up        # start the stack
make down      # stop the stack
```

The test suite is offline and deterministic: it covers image editing, poster
composition, SVG export, storage, LLM response parsing, the pipeline glue (with
network providers stubbed), and the ComfyUI graph builder. CI runs the same two
commands on every push.

### Repository layout

| Path | Purpose |
|---|---|
| `app/` | Streamlit UI and `pipeline.py` (the glue) |
| `app/services/` | One module per provider: `llm`, `imagegen`, `cleanup`, `editor`, `canvas`, `storage` |
| `cleanup-service/` | FastAPI: background removal + upscaling |
| `comfyui-gateway/` | FastAPI: synchronous wrapper around ComfyUI |
| `n8n/` | Importable headless workflow |
| `notebooks/` | Colab notebook: ComfyUI on a free T4 + tunnel |
| `deploy/` | systemd unit, supervisor script, health timer |
| `tests/` | Offline pytest suite |
| `docs/RESOURCES.md` | Catalog of every free/open-source tool, per layer |

Generated files (`logs/`, `app/outputs/`, `.run/`, `.venv/`, `.env`) are never
tracked.

---

## Limitations

- **Colab is time-limited.** Free T4 sessions end; keep Pollinations.ai as the
  fallback (already wired in).
- **Free tiers rate-limit.** Groq, OpenRouter and Pollinations all throttle.
- **Quality/speed is not paid-tier.** Zero budget means best-effort, not
  guaranteed.
- **Upscaling is only "true HD" with a Real-ESRGAN binary.** Otherwise it is
  Lanczos resampling, which is sharp but does not invent detail.

---

## License

[MIT](LICENSE). The bundled tools keep their own licenses (ComfyUI GPL-3.0,
Penpot MPL-2.0, rembg MIT, Real-ESRGAN BSD-3-Clause); see
[`docs/RESOURCES.md`](docs/RESOURCES.md).
