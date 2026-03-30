#!/usr/bin/env bash

# Lightweight launcher for local demo use.
# It prefers the project virtualenv when present and falls back to system python.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python3"

if [[ -x "$VENV_PYTHON" ]]; then
  exec "$VENV_PYTHON" "$ROOT_DIR/scripts/start_demo.py"
fi

exec python3 "$ROOT_DIR/scripts/start_demo.py"
