#!/usr/bin/env bash
set -euo pipefail

echo "==> Checking prerequisites..."
command -v uv >/dev/null 2>&1 || { echo "ERROR: uv not found. Install from https://docs.astral.sh/uv/"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker not found."; exit 1; }

echo "==> Installing Python dependencies..."
uv sync --all-packages

echo "==> Installing pre-commit hooks..."
uv run pre-commit install

echo "==> Starting infrastructure..."
docker compose -f infra/compose/docker-compose.yml up -d

echo "==> Waiting for Postgres to be ready..."
until docker compose -f infra/compose/docker-compose.yml exec -T postgres pg_isready -U podforge -d podforge >/dev/null 2>&1; do
  sleep 2
done

echo "==> Running Alembic migrations..."
(cd apps/api && uv run alembic upgrade head)

echo ""
echo "✓ Setup complete!"
echo ""
echo "Start the API:  cd apps/api && uv run uvicorn podforge_api.main:app --reload"
echo "API docs:       http://localhost:8000/api/docs"
echo "MinIO console:  http://localhost:9001  (minioadmin / minioadmin)"
