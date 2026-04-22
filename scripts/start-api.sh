#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export PYTHONPATH="$REPO_ROOT/apps/api/src:$REPO_ROOT/packages/shared_types/src:$REPO_ROOT/packages/shared_utils/src"

exec "$REPO_ROOT/.venv/bin/uvicorn" podforge_api.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --reload \
  --reload-dir "$REPO_ROOT/apps/api/src" \
  --reload-dir "$REPO_ROOT/packages/shared_types/src" \
  --reload-dir "$REPO_ROOT/packages/shared_utils/src"
