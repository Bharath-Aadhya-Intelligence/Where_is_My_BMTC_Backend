#!/usr/bin/env bash
# One-time setup: venv + dependencies + optional DB seed.
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "Creating virtualenv..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -r requirements.txt

if [[ "${1:-}" == "--seed" ]]; then
  python scripts/seed.py
fi

echo ""
echo "Setup complete. Start the API with:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
