#!/usr/bin/env bash
# Manage the local studio stack:
#   cleanup-service :8000   comfyui-gateway :8100   Streamlit app :8501
#
#   bash start-all.sh            # start (stops any old instance first)
#   bash start-all.sh status     # show what is running
#   bash start-all.sh stop       # stop everything
#   bash start-all.sh restart    # stop then start
#
# Ctrl-C stops everything when running in the foreground.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

RUN_DIR="$HERE/.run"
mkdir -p "$RUN_DIR" logs app/outputs

PORTS=(8000 8100 8501)
NAMES=(cleanup gateway app)

log()  { printf '%s\n' "$*"; }
warn() { printf '%s\n' "$*" >&2; }

port_pid() {  # print the pid listening on port $1, or nothing
  local p="$1" out=""
  if command -v ss >/dev/null 2>&1; then
    out="$(ss -ltnp 2>/dev/null | awk -v pat=":$p\$" '$4 ~ pat' \
           | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)"
  fi
  if [ -z "$out" ] && command -v lsof >/dev/null 2>&1; then
    out="$(lsof -tiTCP:"$p" -sTCP:LISTEN 2>/dev/null | head -1)"
  fi
  printf '%s' "$out"
}

stop() {
  local killed=0
  # 1) pids we recorded
  for n in "${NAMES[@]}"; do
    local f="$RUN_DIR/$n.pid"
    if [ -f "$f" ]; then
      local p; p="$(cat "$f" 2>/dev/null || true)"
      if [ -n "${p:-}" ] && kill "$p" 2>/dev/null; then killed=1; fi
      rm -f "$f"
    fi
  done
  # 2) anything still holding the ports
  for p in "${PORTS[@]}"; do
    local pid; pid="$(port_pid "$p")"
    if [ -n "${pid:-}" ]; then
      kill "$pid" 2>/dev/null || true
      killed=1
    fi
  done
  sleep 2
  # 3) force any stragglers
  for p in "${PORTS[@]}"; do
    local pid; pid="$(port_pid "$p")"
    if [ -n "${pid:-}" ]; then kill -9 "$pid" 2>/dev/null || true; fi
  done
  [ "$killed" = 1 ] && log "stopped old instance(s)." || log "nothing was running."
}

status() {
  local i p pid state url
  for i in "${!PORTS[@]}"; do
    p="${PORTS[$i]}"
    pid="$(port_pid "$p")"
    case "${NAMES[$i]}" in
      cleanup) url="http://127.0.0.1:$p/health" ;;
      gateway) url="http://127.0.0.1:$p/health" ;;
      app)     url="http://127.0.0.1:$p/_stcore/health" ;;
    esac
    if [ -n "${pid:-}" ] && curl -sf -m 3 "$url" >/dev/null 2>&1; then
      state="UP   (pid $pid)"
    elif [ -n "${pid:-}" ]; then
      state="starting/starting-ish (pid $pid)"
    else
      state="DOWN"
    fi
    printf '  %-8s :%s  %s\n' "${NAMES[$i]}" "$p" "$state"
  done
}

wait_up() {  # $1=name  $2=port  $3=health path  $4=pid
  local name="$1" port="$2" path="$3" pid="$4"
  for _ in $(seq 1 30); do
    if curl -sf -m 3 "http://127.0.0.1:$port$path" >/dev/null 2>&1; then
      log "   $name ready"
      return 0
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      warn "   $name exited early — see logs/$name.log"
      return 1
    fi
    sleep 1
  done
  warn "   $name did not become ready in time — see logs/$name.log"
  return 1
}

start() {
  if [ ! -d .venv ]; then
    warn "No .venv found. Run 'bash setup.sh' first."
    exit 1
  fi

  log "checking ports..."
  stop

  # shellcheck disable=SC1091
  source .venv/bin/activate
  if [ -f .env ]; then set -a; . ./.env; set +a; fi

  log "starting services..."
  python cleanup-service/main.py > logs/cleanup.log 2>&1 &
  local p_cleanup=$!; echo "$p_cleanup" > "$RUN_DIR/cleanup.pid"

  python comfyui-gateway/main.py > logs/gateway.log 2>&1 &
  local p_gateway=$!; echo "$p_gateway" > "$RUN_DIR/gateway.pid"

  streamlit run app/app.py --server.port 8501 --server.address 0.0.0.0 \
    --server.headless true > logs/app.log 2>&1 &
  local p_app=$!; echo "$p_app" > "$RUN_DIR/app.pid"

  wait_up cleanup 8000 /health          "$p_cleanup" || true
  wait_up gateway 8100 /health          "$p_gateway" || true
  wait_up app     8501 /_stcore/health  "$p_app"     || true

  log ""
  status
  log ""
  log "Open in your browser:  http://127.0.0.1:8501"
  log "(on this machine use 127.0.0.1; from another device use this machine's LAN IP,"
  log " e.g. http://<this-machine-ip>:8501 — see the 'Network URL' in logs/app.log)"
  log ""
  log "Logs: logs/cleanup.log  logs/gateway.log  logs/app.log"
  log "Stop: bash start-all.sh stop     Status: bash start-all.sh status"

  cleanup_trap() { log ""; log "stopping..."; stop; }
  trap cleanup_trap EXIT INT TERM
  wait
}

case "${1:-start}" in
  start)   start ;;
  stop)    stop ;;
  status)  status ;;
  restart) stop; start ;;
  *) warn "usage: bash start-all.sh [start|stop|status|restart]"; exit 2 ;;
esac
