#!/usr/bin/env bash
set -euo pipefail

echo "==> Running tests..."
(cd apps/api && uv run pytest "$@")
