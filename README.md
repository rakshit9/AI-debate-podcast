# PodForge

Enterprise-grade AI podcast production platform. Give it a topic, get back a full episode — research, debate, voice synthesis, and auto-publishing.

## Quick Start

```bash
# Prerequisites: Docker, uv (https://docs.astral.sh/uv/), pnpm, Node 20+

git clone <repo>
cd podforge
cp .env.example .env  # fill in API keys

./scripts/setup.sh    # installs deps, starts infra, runs migrations

# Start the API
cd apps/api && uv run uvicorn podforge_api.main:app --reload

# API docs (dev only)
open http://localhost:8000/api/docs
```

## Development

```bash
# Lint
./scripts/lint.sh

# Test
./scripts/test.sh

# Infrastructure
docker compose -f infra/compose/docker-compose.yml up -d

# Migrations
cd apps/api && uv run alembic upgrade head
cd apps/api && uv run alembic revision --autogenerate -m "feat: description"
```

## Services

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API docs | http://localhost:8000/api/docs |
| MinIO console | http://localhost:9001 |
| Qdrant | http://localhost:6333 |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) and the project context in [CLAUDE.md](CLAUDE.md).

## License

MIT
