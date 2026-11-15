# RESOURCES — Free & Open-Source Design Ecosystem

The goal of this platform: do every design job — poster, banner, thumbnail, HD
photo — **without a Canva / Photoshop / Midjourney subscription**, from a single
browser, at zero cost. Every tool below is **free** and most are
**open-source**, and the heavy compute runs in the cloud, so an ordinary laptop
is enough.

Each section lists the resource for one layer, the official link, and what it is
for.

---

## 1. Canvas / Layout Layer

Where a design is actually made — text, photo and shapes combined into a poster,
banner or thumbnail.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [Penpot](https://penpot.app) | Yes — open-source (MPL-2.0) | The main canvas. Figma/Canva-like, runs in the browser, self-hostable, SVG-based. |
| [Excalidraw](https://excalidraw.com) | Yes — open-source (MIT) | Fast wireframes, diagrams and sketches. Lightweight and simple. |
| [Krita](https://krita.org) | Yes — open-source (GPL) | Desktop painting and drawing (not browser-based, but free). |
| [Inkscape](https://inkscape.org) | Yes — open-source (GPL) | Vector/SVG editing, logos and print-ready files. |

**Note:** Penpot is the main canvas — run it on the free cloud tier, or
self-host it in Docker on your own machine.

---

## 2. Image Generation Layer

Generating new HD imagery with AI — the free replacement for Midjourney.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Yes — open-source (GPL-3.0) | The main image engine. Node-based workflows, SDXL/Flux support. Runs on a free Google Colab GPU. |
| [Stable Diffusion WebUI (A1111)](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | Yes — open-source (AGPL) | Alternative UI with a large extension ecosystem. |
| [Pollinations.ai](https://pollinations.ai) | Yes — free API | Keyless text-to-image API; the backup when the Colab session ends. |
| [Stable Horde](https://stablehorde.net) | Yes — free, crowdsourced | Distributed free GPU; API key is free. |
| [Hugging Face Spaces](https://huggingface.co/spaces) | Yes — free tier | Host or run ready-made Gradio/ComfyUI demos for free. |
| Flux (Black Forest Labs) | Model — open weights (free APIs exist) | Modern high-quality image model. |

**Note:** Heavy HD generation runs on ComfyUI over Colab's free T4 GPU. Keep a
free API (Pollinations / Stable Horde) as backup — Colab limits sessions.

---

## 3. LLM / Copywriting Layer

Marketing headlines, captions, and the image prompt — all Llama-based.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [Llama (Meta)](https://llama.meta.com) | Model — open weights | The main LLM. Writes headlines, captions and prompts. |
| [Groq](https://console.groq.com) | Yes — free API tier | Runs Llama very fast; free API key. |
| [OpenRouter](https://openrouter.ai) | Yes — free models available | Many models behind one endpoint, including free ones. |
| [Ollama](https://ollama.com) | Yes — open-source (MIT) | Fully offline/local LLM; works without internet. |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Yes — open-source (MIT) | Runs LLMs on CPU too, for lightweight machines. |

**Note:** For a free API, use Groq (fastest) or OpenRouter. For offline use,
Ollama + Llama 3.

---

## 4. Image Utilities Layer

Background removal and clarity/HD enhancement — the neural utilities.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [rembg](https://github.com/danielgatis/rembg) | Yes — open-source (MIT) | Background removal (U2Net) — cuts out a product or person. |
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | Yes — open-source (BSD) | Photo upscaling and clarity enhancement. |
| [GFPGAN](https://github.com/TencentARC/GFPGAN) | Yes — open-source (Apache-2.0) | Face restoration and clarity. |
| [CodeFormer](https://github.com/sczhou/CodeFormer) | Yes — open-source (NTU S-Lab) | Alternative face restoration. |
| [backgroundremover](https://github.com/nadermx/backgroundremover) | Yes — open-source (MIT) | CLI-based background removal for images and video. |
| [Transformers.js](https://github.com/huggingface/transformers.js) | Yes — open-source (Apache-2.0) | Runs models in the browser (WebGPU) — offline background removal/upscaling. |

**Note:** `rembg` and `Real-ESRGAN` live inside `cleanup-service` (FastAPI).
Some of this work can also run in the browser via WebGPU.

---

## 5. Orchestration / Glue Layer

Joining every tool into one **pipeline** — this is the actual product.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [n8n](https://n8n.io) | Yes — self-host free (fair-code/SUL) | The main orchestrator. Webhook trigger plus HTTP Request nodes connect Llama, ComfyUI and cleanup. |
| [FastAPI](https://fastapi.tiangolo.com) | Yes — open-source (MIT) | The API behind `cleanup-service` (rembg/upscale). |
| [Streamlit](https://streamlit.io) | Yes — open-source (Apache-2.0) | The UI of the glue app — type a prompt, press a button, see the result. |
| [Docker Compose](https://docs.docker.com/compose/) | Yes — free | Bring every self-hosted service up with one command. |

**Flow:** Webhook → Llama (prompt/headline) → ComfyUI (image) → rembg (cut out)
→ Real-ESRGAN (HD) → storage → response.

---

## 6. Free Hosting Layer

Keep the heavy work in the cloud — an ordinary laptop still runs the browser.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [Google Colab](https://colab.research.google.com) | Free tier (GPU time-limited) | Heavy ComfyUI image/video generation. |
| [Kaggle Notebooks](https://www.kaggle.com/code) | Free (~30 GPU hours/week) | More free GPU time than Colab, for heavy jobs. |
| [Hugging Face Spaces](https://huggingface.co/spaces) | Free tier | Hosts Gradio/ComfyUI apps: free CPU plus community GPU. |
| [Streamlit Community Cloud](https://streamlit.io/cloud) | Free tier | Hosts the Streamlit glue app for free — push code, it goes live. |
| [Vercel](https://vercel.com) / [Netlify](https://netlify.com) / [Cloudflare Pages](https://pages.cloudflare.com) | Free tier | Free frontend hosting with a fast CDN. |
| [Lightning AI](https://lightning.ai) / [Modal](https://modal.com) / [RunPod](https://runpod.io) | Free credits / serverless GPU | Backup GPU when the Colab session ends. |

---

## 7. Storage / Database Layer

Storing designs and photos, all on free tiers.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [Supabase](https://supabase.com) | Free tier | Postgres database plus file storage and auth. |
| [Cloudflare R2](https://developers.cloudflare.com/r2/) | Free tier | Cheap object storage with free egress. |
| Local disk (self-host) | Yes — free | Keep files on your own laptop/VPS; simplest option. |

---

## 8. Tunnels / Connectivity

Reaching a Colab or remote service from a browser.

| Tool | Free / open-source? | Why / what for |
|---|---|---|
| [cloudflared](https://github.com/cloudflare/cloudflared) | Yes — free (Cloudflare) | Exposes the Colab ComfyUI port as a public URL you can open locally. |
| [ngrok](https://ngrok.com) | Free tier | Alternative tunnel (rate-limited). |

---

## 9. Reality check (limitations)

- **Colab time limit:** a free T4 is available for only a few hours a day — it is
  not a 24/7 host. Keep a backup API (Pollinations / Stable Horde).
- **Free-tier rate limits:** every free service throttles under heavy use.
- **Quality/speed trade-off:** at zero cost, speed and HD quality will not match
  a paid tier.
- **Penpot self-hosting:** self-hosting needs a server running Docker; for a
  fully zero-cost setup use the free cloud tier or local Docker.
- **No capable GPU:** all image/video work happens in the cloud, and the laptop
  only runs the browser.

---

## Bottom line

> **Penpot = canvas, ComfyUI (Colab) = image, Llama (Groq) = copy, rembg +
> Real-ESRGAN = cleanup, n8n = glue, free cloud = host.** The real work is not
> building the tools — it is **wiring them into one flow**.
