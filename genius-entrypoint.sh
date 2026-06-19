#!/bin/sh
set -e

if [ -f /opt/genius/patch_branding.py ] && [ -f /opt/genius/logo-icon.png ]; then
  python3 /opt/genius/patch_branding.py 2>/dev/null || true
fi

exec /compose/start "$@"
