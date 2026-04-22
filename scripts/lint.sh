#!/usr/bin/env bash
set -euo pipefail

echo "==> Ruff check..."
uv run ruff check .

echo "==> Ruff format check..."
uv run ruff format --check .

echo "==> mypy..."
uv run mypy apps/api/src --config-file apps/api/pyproject.toml

echo "✓ All lint checks passed."
