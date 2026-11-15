# Cleanup Service

Small FastAPI microservice that does the two "photo fix-up" jobs of the design
studio, on CPU, with no paid API:

| Method | Path         | Input                                   | Output      |
|--------|--------------|-----------------------------------------|-------------|
| GET    | `/health`    | –                                       | `{"status":"ok"}` |
| POST   | `/remove-bg` | multipart field `file`                  | `image/png` (transparent background) |
| POST   | `/upscale`   | multipart field `file`, query `scale`   | `image/png` (HD) |

## Engines

- **Background removal** uses [`rembg`](https://github.com/danielgatis/rembg)
  (U²-Net). Model selectable with `REMBG_MODEL` (default `u2net`).
- **Upscaling** tries, in order:
  1. `realesrgan-ncnn-vulkan` binary if `SR_BIN` points at it,
  2. the pip-installable `realesrgan`/`basicsr` stack if installed,
  3. a Pillow LANCZOS resize — so the endpoint **always** answers.

## Run

```bash
pip install -r requirements.txt
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000
```

Docker:

```bash
docker build -t design-cleanup .
docker run --rm -p 8000:8000 design-cleanup
```

## Environment

| Variable      | Default | Meaning                                    |
|---------------|---------|--------------------------------------------|
| `PORT`        | `8000`  | HTTP port                                  |
| `REMBG_MODEL` | `u2net` | rembg model name                           |
| `SR_BIN`      | empty   | path to `realesrgan-ncnn-vulkan` (optional) |

## Example

```bash
curl -F file=@photo.jpg http://localhost:8000/remove-bg -o no-bg.png
curl -F file=@photo.jpg "http://localhost:8000/upscale?scale=2" -o hd.png
```
