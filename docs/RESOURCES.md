# RESOURCES — Free & Open-Source Design Ecosystem

Yo platform ko uddeshya: **Canva / Photoshop / Midjourney ko subscription bina**, Rs. 0 ma sabai design kaam — poster, banner, thumbnail, HD photo — eutai browser bata. Sabai tool **free** ra dherai **open-source** chan, ani heavy kaam cloud ma hunchha (weak laptop ma pani chalchha).

Tala sabai layer ma chahine resource, official link, ra kasko lagi ho tyo dinya chha.

---

## 1. Canvas / Layout Layer

Design banaune mukhya thau — text, photo, shape milaera poster/banner/thumbnail banaune.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [Penpot](https://penpot.app) | Ho — open-source (MPL-2.0) | Mukhya canvas. Figma/Canva jasto, browser ma chalchha, self-host garna milchha. SVG-based. |
| [Excalidraw](https://excalidraw.com) | Ho — open-source (MIT) | Chhito wireframe/diagram/sketch ko lagi. Haluko ra simple. |
| [Krita](https://krita.org) | Ho — open-source (GPL) | Desktop ma painting/drawing (browser hoina, tara free). |
| [Inkscape](https://inkscape.org) | Ho — open-source (GPL) | Vector/SVG editing, logo ra print file ko lagi. |

**Note:** Penpot nai mukhya canvas ho — yaslai free cloud ma chalaune, wa Docker bata afnai laptop/PC ma self-host garne.

---

## 2. Image Generation Layer

AI bata naya HD photo banaune — Midjourney ko free replacement.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Ho — open-source (GPL-3.0) | Mukhya image engine. Node-based workflow, SDXL/Flux support. Google Colab ko free GPU ma chalcha. |
| [Stable Diffusion WebUI (A1111)](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | Ho — open-source (AGPL) | Alternative UI, dherai extension. |
| [Pollinations.ai](https://pollinations.ai) | Ho — free API | Text-to-image free API, Colab limit sakida backup. |
| [Stable Horde](https://stablehorde.net) | Ho — free crowdsourced | Distributed free GPU, API key free. |
| [Hugging Face Spaces](https://huggingface.co/spaces) | Ho — free tier | Ready-made Gradio/ComfyUI demo free ma host/chalau. |
| Flux (Black Forest Labs) | Model — open weights (katai free API) | Modern high-quality image model. |

**Note:** Heavy HD generation Colab ko free T4 GPU ma ComfyUI le garchha. Free API (Pollinations / Stable Horde) backup rakhnu — Colab dindin limit hunchha.

---

## 3. LLM / Copywriting Layer

Marketing headline, caption, ra image ya prompt lekhne — Llama based.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [Llama (Meta)](https://llama.meta.com) | Model — open weights | Mukhya LLM. Headline/caption/prompt lekhchha. |
| [Groq](https://console.groq.com) | Ho — free API tier | Llama dherai chhito chalau, free API key. |
| [OpenRouter](https://openrouter.ai) | Ho — free models available | Eutai endpoint bata dherai model, free model use garna milchha. |
| [Ollama](https://ollama.com) | Ho — open-source (MIT) | Offline/local LLM, internet chhaina pani chalchha. |
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | Ho — open-source (MIT) | CPU ma pani LLM chalaune, haluko machine ko lagi. |

**Note:** Satto sat free API = Groq (chhito) wa OpenRouter. Offline = Ollama + Llama 3.

---

## 4. Image Utilities Layer

Background hataune ra clarity/HD banaune — neural utilities.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [rembg](https://github.com/danielgatis/rembg) | Ho — open-source (MIT) | Background remove (U2Net) — product/person ko bg hataune. |
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | Ho — open-source (BSD) | Photo upscale / clarity badhaune. |
| [GFPGAN](https://github.com/TencentARC/GFPGAN) | Ho — open-source (Apache-2.0) | Anuhar restore / face clarity. |
| [CodeFormer](https://github.com/sczhou/CodeFormer) | Ho — open-source (NTU S-Lab) | Face restoration alternative. |
| [backgroundremover](https://github.com/nadermx/backgroundremover) | Ho — open-source (MIT) | CLI-based bg remove + video bg remove. |
| [Transformers.js](https://github.com/huggingface/transformers.js) | Ho — open-source (Apache-2.0) | Browser mai (WebGPU) model chalau — offline bg remove/upscale. |

**Note:** `rembg` ra `Real-ESRGAN` cleanup-service vitra thapinchha (FastAPI). Kati kaam browser mai WebGPU bata pani hunu sakchha.

---

## 5. Orchestration / Glue Layer

Sabai tool lai eutai **pipeline** ma jodne — asli "mukhya kaam" yahi ho.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [n8n](https://n8n.io) | Ho — self-host free (fair-code/SUL) | Mukhya orchestrator. Webhook trigger, HTTP Request node bata Llama/ComfyUI/cleanup jodchha. |
| [FastAPI](https://fastapi.tiangolo.com) | Ho — open-source (MIT) | Cleanup-service (rembg/upscale) ko API. |
| [Streamlit](https://streamlit.io) | Ho — open-source (Apache-2.0) | Glue app ko UI — prompt lekha, button thich, result herna. |
| [Docker Compose](https://docs.docker.com/compose/) | Ho — free | Sabai self-host service eutai command ma khadaune. |

**Flow:** Webhook → Llama (prompt/headline) → ComfyUI (image) → rembg (bg hata) → Real-ESRGAN (HD) → storage → response.

---

## 6. Free Hosting Layer

Sabai heavy kaam cloud ma rakhne — sadhaaran laptop ma pani chalchha.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [Google Colab](https://colab.research.google.com) | Free tier (GPU time-limited) | ComfyUI heavy image/video generation. |
| [Kaggle Notebooks](https://www.kaggle.com/code) | Free (~30 hrs/week GPU) | Colab bhanda badi free GPU time, heavy kaam. |
| [Hugging Face Spaces](https://huggingface.co/spaces) | Free tier | Gradio/ComfyUI app host, CPU free + community GPU. |
| [Streamlit Community Cloud](https://streamlit.io/cloud) | Free tier | Glue app (Streamlit) free host — code push = live. |
| [Vercel](https://vercel.com) / [Netlify](https://netlify.com) / [Cloudflare Pages](https://pages.cloudflare.com) | Free tier | Frontend free host + fast CDN. |
| [Lightning AI](https://lightning.ai) / [Modal](https://modal.com) / [RunPod](https://runpod.io) | Free credits / serverless GPU | Colab limit sakida backup GPU. |

---

## 7. Storage / Database Layer

Design ra photo rakhna, sabai free tier.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [Supabase](https://supabase.com) | Free tier | Postgres DB + file storage, auth pani. |
| [Cloudflare R2](https://developers.cloudflare.com/r2/) | Free tier | Sasto object storage, egress free. |
| Local disk (self-host) | Ho — free | Afnai laptop/VPS ma file rakhne, simple. |

---

## 8. Tunnels / Connectivity

Colab/remote service lai browser bata connect garna.

| Tool | Free/Open-source? | Kina / Kasko lagi |
|---|---|---|
| [cloudflared](https://github.com/cloudflare/cloudflared) | Ho — free (Cloudflare) | Colab ko ComfyUI port lai public URL ma kholne, timro browser bata chalau. |
| [ngrok](https://ngrok.com) | Free tier | Alternative tunnel (limit chha). |

---

## 9. Yatharth (Limitations — sachho kura)

- **Colab time limit:** Free T4 din ko kehi ghanta matra — 24/7 bhar pardaina. Backup free API (Pollinations / Stable Horde) rakhnu.
- **Free tier rate limit:** Dherai use gare si sabai free service ma limit aauchha.
- **Quality/speed trade-off:** Rs. 0 ma speed ra HD quality paid jasto ramro nahuna sakchha.
- **Penpot self-host:** Self-host garna server (Docker) chahinchha; pura zero-cost ko lagi free cloud tier wa local Docker.
- **GPU thik chhaina bhanne:** Sabai image/video kaam cloud ma, timro laptop ma khali browser.

---

## Nicha

> **Penpot = canvas, ComfyUI (Colab) = photo, Llama (Groq) = lekha, rembg + Real-ESRGAN = safa, n8n = jodne, ani free cloud = host.** Asli kaam tool banaunu hoina — **sabai jodera eutai flow** banaunu ho.
