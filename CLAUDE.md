# PodForge — Claude Code Context

## Repo structure

```
podforge/
├── apps/api/          # FastAPI backend (podforge-api)
├── apps/web/          # Next.js 15 frontend (Phase 5)
├── apps/cli/          # Python CLI (podforge-cli)
├── services/agents/   # LangGraph + AutoGen orchestration (Phase 3)
├── services/mcp/      # 5 MCP servers (Phase 2)
├── packages/shared_types/   # Pydantic enums/types used across all packages
├── packages/shared_utils/   # Logging, shared helpers
├── infra/compose/     # docker-compose.yml
├── infra/docker/      # Dockerfiles
└── scripts/           # setup.sh, lint.sh, test.sh
```

## uv workspace

Root `pyproject.toml` declares the workspace. Members:
- `apps/api` → `podforge-api`
- `apps/cli` → `podforge-cli`
- `packages/shared_types` → `podforge-shared-types`
- `packages/shared_utils` → `podforge-shared-utils`

**Add a dep to the API:** `uv add <pkg> --package podforge-api`
**Add a workspace dep:** declare in pyproject.toml `[tool.uv.sources]` with `{ workspace = true }`
**Sync all:** `uv sync --all-packages`

## Key commands

```bash
# Start infra
docker compose -f infra/compose/docker-compose.yml up -d

# Run API
cd apps/api && uv run uvicorn podforge_api.main:app --reload

# Migrations
cd apps/api && uv run alembic upgrade head
cd apps/api && uv run alembic revision --autogenerate -m "feat: ..."

# Tests
cd apps/api && uv run pytest

# Lint
uv run ruff check . && uv run ruff format --check .
uv run mypy apps/api/src --config-file apps/api/pyproject.toml
```

## Where things live

| Task | Location |
|------|----------|
| New API endpoint | `apps/api/src/podforge_api/routers/` |
| New DB model | `apps/api/src/podforge_api/models/` + alembic revision |
| Business logic | `apps/api/src/podforge_api/services/` |
| Shared enums | `packages/shared_types/src/podforge_shared_types/enums.py` |
| Agent pipeline | `services/agents/src/podforge_agents/graphs/` (Phase 3) |
| MCP tools | `services/mcp/<server>/` (Phase 2) |
| Celery tasks | `apps/api/src/podforge_api/workers/` |

## Non-negotiables

- `uv` only (no pip/poetry)
- `mypy --strict` must pass
- `ruff check` + `ruff format` must pass
- Pydantic v2 — use `model_config = ConfigDict(from_attributes=True)` not `orm_mode`
- SQLAlchemy 2.0 — use `Mapped[T]` + `mapped_column()`, never legacy patterns
- Async everywhere — `AsyncSession`, `async def` routes, no blocking I/O
- Prompts in files (`services/agents/src/podforge_agents/prompts/`), never inline
- All LLM calls through LangSmith (Phase 3+)
- MCP for all external integrations (Phase 2+)
- Secrets in `.env` only, never committed

## Known gaps (Phase 1)

- Refresh token rotation not implemented (tokens are stateless JWT — no revocation)
- API key lookup does full table scan — add index or Redis cache in Phase 2
- CORS is wide open (`allow_origins=["*"]`) — lock down before production
