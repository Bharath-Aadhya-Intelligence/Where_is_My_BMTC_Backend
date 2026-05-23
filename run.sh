#!/usr/bin/env bash
# Run the API using the project virtualenv (avoids system Python missing deps).
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "Creating virtualenv..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -r requirements.txt

exec uvicorn app.main:app --reload --host 0.0.0.0 --port "${PORT:-8000}"
