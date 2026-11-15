# n8n — Zero-Budget Design Pipeline

The orchestration (glue) layer for the design studio. It chains the free tools
into one pipeline:

```
Webhook (POST /design)
  -> Llama Copy + Prompt   (Groq, OpenAI-compatible)
  -> ComfyUI Generate      (comfyui-gateway /generate — free Colab GPU)
  -> Remove Background     (cleanup-service /remove-bg, rembg)
  -> Upscale               (cleanup-service /upscale, Real-ESRGAN)
  -> Respond to Webhook    (final PNG back to the caller)
```

## Import

1. Open your n8n instance.
2. **Workflows → Add workflow → ⋯ (top right) → Import from File**.
3. Select `n8n/workflows/design-pipeline.json`.
4. The workflow imports inactive — configure the credential and env vars below,
   then activate it.

## 1. Credentials

Create one **Header Auth** credential and attach it to the
**Llama Copy + Prompt** node (replace the `Groq account` placeholder):

| Field        | Value               |
| ------------ | ------------------- |
| Header Name  | `Authorization`     |
| Header Value | `Bearer <GROQ_KEY>` |

Get a free key at <https://console.groq.com/keys>.

## 2. Environment variables

`$env` access must be enabled: set `N8N_BLOCK_ENV_ACCESS_IN_NODE=false`
on the n8n process. Then set:

| Variable              | Example                          | Used for                                     |
| --------------------- | -------------------------------- | -------------------------------------------- |
| `GROQ_MODEL`          | `llama-3.3-70b-versatile`        | Llama model that writes headline + prompt    |
| `COMFYUI_GATEWAY_URL` | `http://comfyui-gateway:8100`    | Synchronous gateway in front of ComfyUI      |
| `CLEANUP_URL`         | `http://cleanup-service:8000`    | The rembg / Real-ESRGAN FastAPI service      |

`COMFYUI_GATEWAY_URL` is the local gateway, not the Colab URL — the gateway
itself holds `COMFYUI_URL` (the Colab tunnel URL). See `../comfyui-gateway/`.

## 3. Trigger

```bash
curl -X POST "$N8N_WEBHOOK_URL/design" \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "nepali festival dashain sale poster, warm colors"}' \
  -o design.png
```

The response is the final image (background removed + upscaled).

## Why a gateway instead of calling ComfyUI directly

Stock ComfyUI `/prompt` is **asynchronous**: it returns only a `prompt_id`, and
the PNG is written later into ComfyUI's `output/` folder, fetched from `/view`.
n8n's HTTP nodes expect a direct response, so the **ComfyUI Generate** node calls
`comfyui-gateway`'s synchronous `POST /generate` instead, which does the
submit → poll → fetch internally and returns the finished PNG immediately.
