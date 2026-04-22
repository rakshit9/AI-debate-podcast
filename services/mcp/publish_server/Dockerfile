FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages/shared_types/ packages/shared_types/
COPY packages/shared_utils/ packages/shared_utils/
COPY services/mcp/publish_server/ services/mcp/publish_server/

RUN uv sync --package podforge-publish-mcp --no-dev --frozen

CMD ["uv", "run", "--package", "podforge-publish-mcp", "publish-mcp"]
