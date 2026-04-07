#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$ROOT_DIR/tailwindcss" \
  -i "$ROOT_DIR/disagro_p/static/css/tailwind.input.css" \
  -o "$ROOT_DIR/disagro_p/static/css/tailwind.css" \
  --minify \
  --cwd "$ROOT_DIR"
