#!/bin/sh
set -e

if [ -f /opt/genius/patch_branding.py ] && [ -f /opt/genius/logo-icon.png ]; then
  python3 /opt/genius/patch_branding.py 2>/dev/null || true
fi

PUBLIC_PORT="${PORT:-8000}"
POSTHOG_PORT=8080

sed \
  -e "s/__LISTEN_PORT__/${PUBLIC_PORT}/g" \
  -e "s/__POSTHOG_PORT__/${POSTHOG_PORT}/g" \
  /opt/genius/nginx.conf.template > /etc/nginx/nginx.conf

if ! nginx -t 2>/tmp/nginx-test.log; then
  cat /tmp/nginx-test.log >&2
  exit 1
fi

export PORT="${POSTHOG_PORT}"
/compose/start "$@" &
POSTHOG_PID=$!

ready=0
i=0
while [ "$i" -lt 120 ]; do
  if curl -sf "http://127.0.0.1:${POSTHOG_PORT}/login" >/dev/null 2>&1; then
    ready=1
    break
  fi
  if ! kill -0 "$POSTHOG_PID" 2>/dev/null; then
    echo "PostHog process exited before becoming ready" >&2
    wait "$POSTHOG_PID" || true
    exit 1
  fi
  i=$((i + 1))
  sleep 2
done

if [ "$ready" -ne 1 ]; then
  echo "PostHog did not become ready in time" >&2
  kill "$POSTHOG_PID" 2>/dev/null || true
  exit 1
fi

echo "PostHog ready on :${POSTHOG_PORT}; nginx listening on :${PUBLIC_PORT}"
exec nginx -g 'daemon off;'
