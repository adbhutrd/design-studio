#!/usr/bin/env bash
# Install the studio as a persistent systemd USER service (+ health timer).
#
#   bash deploy/install-service.sh     # install + start + enable on boot/login
#   bash deploy/uninstall-service.sh   # remove (see below / this script --uninstall)
#
# User services keep running after you log out because Linger is enabled for
# this account (`loginctl show-user $USER -p Linger` -> Linger=yes).
set -euo pipefail

STUDIO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

UNITS=(design-studio.service design-studio-health.service design-studio-health.timer)

uninstall() {
  systemctl --user disable --now design-studio-health.timer 2>/dev/null || true
  systemctl --user disable --now design-studio.service 2>/dev/null || true
  for u in "${UNITS[@]}"; do rm -f "$UNIT_DIR/$u"; done
  systemctl --user daemon-reload
  systemctl --user reset-failed 2>/dev/null || true
  echo "uninstalled. (the studio is no longer auto-started)"
}

if [ "${1:-}" = "--uninstall" ]; then uninstall; exit 0; fi

echo "==> Stopping any hand-started stack so the service can own the ports"
bash "$STUDIO_DIR/start-all.sh" stop >/dev/null 2>&1 || true

mkdir -p "$UNIT_DIR"
for u in "${UNITS[@]}"; do
  sed "s|@STUDIO_DIR@|$STUDIO_DIR|g" "$STUDIO_DIR/deploy/$u" > "$UNIT_DIR/$u"
  echo "    wrote $UNIT_DIR/$u"
done

echo "==> Enabling + starting"
systemctl --user daemon-reload
systemctl --user enable --now design-studio.service
systemctl --user enable --now design-studio-health.timer

sleep 8
echo
systemctl --user --no-pager status design-studio.service | head -12 || true
echo
echo "Installed. Useful commands:"
echo "  systemctl --user status design-studio"
echo "  systemctl --user restart design-studio"
echo "  systemctl --user stop design-studio"
echo "  journalctl --user -u design-studio -f"
echo "  systemctl --user list-timers design-studio-health.timer"
