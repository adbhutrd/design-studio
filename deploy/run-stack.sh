#!/usr/bin/env bash
# Foreground supervisor for the design studio stack, meant to be run BY systemd.
#
#   design-studio.service -> this script -> cleanup-service + gateway + app
#
# It stays in the foreground and exits as soon as ANY child dies, so systemd's
# Restart=always brings the whole stack back up. (systemd manages restart, this
# script just supervises.)
set -uo pipefail

STUDIO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$STUDIO_DIR"
mkdir -p logs app/outputs

# shellcheck disable=SC1091
source "$STUDIO_DIR/.venv/bin/activate"
if [ -f .env ]; then set -a; . ./.env; set +a; fi

PIDS=()
stop_children() {
  for pid in "${PIDS[@]:-}"; do kill "$pid" 2>/dev/null || true; done
  wait 2>/dev/null || true
}
trap stop_children EXIT INT TERM

echo "[design-studio] starting cleanup-service :8000"
python cleanup-service/main.py > logs/cleanup.log 2>&1 &
PIDS+=($!)

echo "[design-studio] starting comfyui-gateway :8100"
python comfyui-gateway/main.py > logs/gateway.log 2>&1 &
PIDS+=($!)

echo "[design-studio] starting streamlit app :8501"
streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0 \
  --server.headless true > logs/app.log 2>&1 &
PIDS+=($!)

# Block until any one service exits, then exit non-zero so systemd restarts us.
wait -n "${PIDS[@]}"
rc=$?
echo "[design-studio] a service exited (rc=$rc) — asking systemd to restart the stack"
exit "$rc"
