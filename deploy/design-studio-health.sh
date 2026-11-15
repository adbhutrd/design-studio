#!/usr/bin/env bash
# Health monitor for the design studio stack.
#
# Runs from design-studio-health.timer every couple of minutes. If any of the
# three endpoints stops answering, it restarts design-studio.service. This catches
# the case where the supervisor itself is wedged but still "running".
set -uo pipefail

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

STUDIO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="$STUDIO_DIR/logs/health.log"
mkdir -p "$STUDIO_DIR/logs"

check() { curl -sf -m 5 "$1" >/dev/null 2>&1; }

problems=""
check "http://127.0.0.1:8501/_stcore/health" || problems="$problems app"
check "http://127.0.0.1:8000/health"          || problems="$problems cleanup"
check "http://127.0.0.1:8100/health"          || problems="$problems gateway"

stamp="$(date '+%Y-%m-%d %H:%M:%S')"

if [ -z "$problems" ]; then
  echo "$stamp OK (app, cleanup, gateway)" >> "$LOG"
  exit 0
fi

echo "$stamp UNHEALTHY:$problems -> restarting design-studio.service" >> "$LOG"
systemctl --user restart design-studio.service
exit 0
