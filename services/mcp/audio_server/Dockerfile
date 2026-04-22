FROM python:3.11-slim

# ffmpeg required by pydub for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages/shared_types/ packages/shared_types/
COPY packages/shared_utils/ packages/shared_utils/
COPY services/mcp/audio_server/ services/mcp/audio_server/

RUN uv sync --package podforge-audio-mcp --no-dev --frozen

CMD ["uv", "run", "--package", "podforge-audio-mcp", "audio-mcp"]
