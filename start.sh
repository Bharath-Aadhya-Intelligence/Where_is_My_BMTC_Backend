#!/usr/bin/env bash
# Render sets PORT automatically. Do not hardcode 8000 in production.
set -euo pipefail

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
WORKERS="${WEB_CONCURRENCY:-1}"

echo "Starting Where Is My BMTC API on ${HOST}:${PORT} (workers=${WORKERS})"

if [[ "${WORKERS}" -gt 1 ]]; then
  exec gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    -w "${WORKERS}" \
    -b "${HOST}:${PORT}" \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile -
else
  exec uvicorn app.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --proxy-headers \
    --forwarded-allow-ips='*'
fi
