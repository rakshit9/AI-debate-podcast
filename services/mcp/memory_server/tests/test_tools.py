from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_get_host_memory_returns_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")

    mock_embedding = [0.1] * 1536

    mock_hit = MagicMock()
    mock_hit.payload = {"content": "Host likes debates", "host_id": "host-1"}
    mock_hit.score = 0.95

    with (
        patch(
            "podforge_memory_mcp.tools.vectors._get_embedding",
            new_callable=AsyncMock,
            return_value=mock_embedding,
        ),
        patch("podforge_memory_mcp.tools.vectors.AsyncQdrantClient") as mock_qdrant_cls,
    ):
        mock_qdrant = AsyncMock()
        mock_qdrant.get_collection = AsyncMock()
        mock_qdrant.search.return_value = [mock_hit]
        mock_qdrant_cls.return_value = mock_qdrant

        from podforge_memory_mcp.tools.vectors import get_host_memory

        results = await get_host_memory("host-1", "debate style", k=3)

    assert len(results) == 1
    assert results[0]["content"] == "Host likes debates"
    assert results[0]["score"] == 0.95


@pytest.mark.asyncio
async def test_update_host_memory_upserts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")

    mock_embedding = [0.2] * 1536

    with (
        patch(
            "podforge_memory_mcp.tools.vectors._get_embedding",
            new_callable=AsyncMock,
            return_value=mock_embedding,
        ),
        patch("podforge_memory_mcp.tools.vectors.AsyncQdrantClient") as mock_qdrant_cls,
    ):
        mock_qdrant = AsyncMock()
        mock_qdrant.get_collection = AsyncMock()
        mock_qdrant.upsert = AsyncMock()
        mock_qdrant_cls.return_value = mock_qdrant

        from podforge_memory_mcp.tools.vectors import update_host_memory

        await update_host_memory("host-1", "Host prefers calm debates")

    mock_qdrant.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_get_show_style_guide_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://podforge:podforge@localhost:5432/podforge",
    )

    mock_conn = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = ("Be conversational and engaging.",)
    mock_conn.execute.return_value = mock_result
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)

    mock_engine = MagicMock()
    mock_engine.begin.return_value = mock_conn
    mock_engine.dispose = AsyncMock()

    with patch(
        "podforge_memory_mcp.tools.metadata.create_async_engine",
        return_value=mock_engine,
    ):
        from podforge_memory_mcp.tools.metadata import get_show_style_guide

        guide = await get_show_style_guide("show-123")

    assert guide == "Be conversational and engaging."
