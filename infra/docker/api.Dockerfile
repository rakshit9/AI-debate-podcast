FROM python:3.11-slim AS builder
WORKDIR /build

RUN pip install uv

COPY pyproject.toml ./
COPY packages/ packages/
COPY apps/api/ apps/api/

RUN uv sync --no-dev --package podforge-api

FROM python:3.11-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/.venv /app/.venv
COPY apps/api/src /app/src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "podforge_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
