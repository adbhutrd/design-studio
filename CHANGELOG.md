# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-11-15

First public release: the zero-budget design platform as a self-contained,
documented project.

### Added

- Streamlit app with two modes: AI generation and photo upload/editing.
- `cleanup-service` (FastAPI): `POST /remove-bg` via rembg, `POST /upscale` with a
  three-engine chain (Real-ESRGAN binary → Python package → Pillow Lanczos).
- `comfyui-gateway` (FastAPI): synchronous `POST /generate` in front of ComfyUI.
- Pipeline glue with graceful degradation across LLM and image providers.
- Poster composer and Penpot-importable SVG export.
- n8n workflow that runs the same pipeline headlessly.
- Colab notebook for a free-GPU ComfyUI instance behind a Cloudflare tunnel.
- systemd user service, supervisor script and health timer for always-on use.
- Docker Compose stack for app + n8n + both side services.
- Offline pytest suite, ruff configuration and GitHub Actions CI.
- Project documents: README, CONTRIBUTING, SECURITY, LICENSE (MIT).
