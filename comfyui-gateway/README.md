# ComfyUI Gateway

Turns ComfyUI's **asynchronous** API into one **synchronous** call, so the app
and n8n can ask for an image and get PNG bytes back directly.

ComfyUI's stock `POST /prompt` only returns a `prompt_id`; the finished PNG lands
in its `output/` folder and must be polled from `/history` and fetched from
`/view`. This service owns that submit → poll → fetch logic exactly once, which
is why both the Streamlit app and the n8n workflow point at it.

| Method | Path        | Input                                             | Output              |
|--------|-------------|---------------------------------------------------|---------------------|
| GET    | `/health`   | –                                                 | `{"status": ...}`   |
| POST   | `/generate` | JSON: `prompt`, `negative_prompt`, `width`, `height`, `steps`, `cfg`, `seed`, `ckpt` | `image/png` |

## Run

```bash
pip install -r requirements.txt
COMFYUI_URL=https://xxxx.trycloudflare.com python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8100
```

## Environment

| Variable                | Default                          | Meaning                                  |
|-------------------------|----------------------------------|------------------------------------------|
| `PORT`                  | `8100`                           | HTTP port                                |
| `COMFYUI_URL`           | `http://127.0.0.1:8188`          | ComfyUI base URL (Colab tunnel URL)      |
| `COMFYUI_CKPT`          | `sd_xl_base_1.0.safetensors`     | Checkpoint ComfyUI loads                 |
| `COMFYUI_POLL_INTERVAL` | `2`                              | Seconds between `/history` polls         |
| `COMFYUI_TIMEOUT`       | `300`                            | Give up after this many seconds          |

## Example

```bash
curl -X POST http://localhost:8100/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "dashain sale poster, warm colors", "width": 1024, "height": 1024}' \
  -o poster.png
```
