# ComfyUI on Colab

Open `comfyui_colab.ipynb` in Google Colab (Runtime → Change runtime type → Hardware accelerator → GPU/T4), then **Run all**.

When the last cell prints a `https://<random>.trycloudflare.com` URL, copy it and set it as `COMFYUI_URL` in the platform's `.env` (see `../../.env.example`).

The URL changes every run, so re-copy it into `COMFYUI_URL` whenever you restart Colab.

If no GPU is available or the session ends, the platform automatically falls back to the free cloud APIs configured in `.env`.
