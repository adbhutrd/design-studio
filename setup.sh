#!/usr/bin/env bash
# Local setup for Open Design Studio (no Docker, no GPU required).
# Creates a virtualenv, installs the app + cleanup-service, and prepares .env.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PY="${PYTHON:-python3}"

echo "==> Checking Python"
"$PY" --version

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> Created .env from .env.example — add your free API keys to it."
else
  echo "==> .env already exists, leaving it untouched."
fi

echo "==> Creating virtualenv (.venv)"
"$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing app dependencies"
pip install --quiet --upgrade pip
pip install --quiet -r app/requirements.txt

echo "==> Installing cleanup-service dependencies (rembg is a large download)"
pip install --quiet -r cleanup-service/requirements.txt

cat <<'EOF'

Done. Next steps:
  1. Put a free Groq key in .env:            GROQ_API_KEY=...
  2. Start the cleanup service:              (venv) python cleanup-service/main.py
  3. Start the sync gateway (needs Colab):   (venv) COMFYUI_URL=<colab-url> python comfyui-gateway/main.py
  4. Start the app:                          (venv) streamlit run app/app.py

Or run everything with Docker:  docker compose up -d
EOF
