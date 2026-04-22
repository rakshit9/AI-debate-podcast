import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from podforge_research_mcp.tools import arxiv_tool, news, reader, youtube
from podforge_research_mcp.tools.web import search_web


@pytest.mark.asyncio
async def test_search_web_returns_cached_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")

    cached_data: list[dict[str, Any]] = [
        {"url": "https://example.com", "title": "Test", "content": "body", "score": 0.9}
    ]

    mock_r = AsyncMock()
    mock_r.get.return_value = json.dumps(cached_data)
    mock_r.__aenter__ = AsyncMock(return_value=mock_r)
    mock_r.__aexit__ = AsyncMock(return_value=False)

    with patch("podforge_research_mcp.tools.web.aioredis.from_url", return_value=mock_r):
        results = await search_web("AI debate", 5)

    assert len(results) == 1
    assert results[0]["title"] == "Test"


@pytest.mark.asyncio
async def test_search_web_calls_tavily_on_cache_miss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")

    tavily_response = {
        "results": [{"url": "https://tavily.com", "title": "Tavily", "content": "c", "score": 0.8}]
    }

    mock_r = AsyncMock()
    mock_r.get.return_value = None
    mock_r.setex = AsyncMock()
    mock_r.__aenter__ = AsyncMock(return_value=mock_r)
    mock_r.__aexit__ = AsyncMock(return_value=False)

    mock_tavily = AsyncMock()
    mock_tavily.search.return_value = tavily_response

    with (
        patch("podforge_research_mcp.tools.web.aioredis.from_url", return_value=mock_r),
        patch(
            "podforge_research_mcp.tools.web.AsyncTavilyClient",
            return_value=mock_tavily,
        ),
    ):
        results = await search_web("new topic", 3)

    assert results[0]["title"] == "Tavily"
    mock_r.setex.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_arxiv_returns_papers() -> None:
    mock_result = MagicMock()
    mock_result.title = "AI Research"
    mock_result.authors = ["Alice", "Bob"]
    mock_result.summary = "Abstract text"
    mock_result.entry_id = "https://arxiv.org/abs/1234"
    mock_result.published.isoformat.return_value = "2024-01-01T00:00:00"
    mock_result.pdf_url = "https://arxiv.org/pdf/1234"

    with patch("podforge_research_mcp.tools.arxiv_tool.arxiv") as mock_arxiv:
        mock_client = MagicMock()
        mock_client.results.return_value = [mock_result]
        mock_arxiv.Client.return_value = mock_client
        mock_arxiv.Search.return_value = MagicMock()
        mock_arxiv.SortCriterion.Relevance = "relevance"

        papers = await arxiv_tool.fetch_arxiv("large language models", 2)

    assert len(papers) == 1
    assert papers[0]["title"] == "AI Research"


@pytest.mark.asyncio
async def test_fetch_youtube_transcripts_handles_error() -> None:
    with patch(
        "podforge_research_mcp.tools.youtube.YouTubeTranscriptApi.get_transcript",
        side_effect=Exception("network error"),
    ):
        results = await youtube.fetch_youtube_transcripts(["bad_id"])

    assert results[0]["error"] == "network error"
    assert results[0]["transcript"] == ""


@pytest.mark.asyncio
async def test_read_url_returns_content() -> None:
    with patch("podforge_research_mcp.tools.reader.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "<html>Hello</html>"
        mock_response.raise_for_status = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        content = await reader.read_url("https://example.com")

    assert "Hello" in content


@pytest.mark.asyncio
async def test_get_news_today_returns_articles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEWSAPI_KEY", "test-key")

    mock_articles = [
        {
            "title": "Breaking News",
            "source": {"name": "BBC"},
            "url": "https://bbc.com",
            "description": "Desc",
            "publishedAt": "2024-01-01T00:00:00Z",
        }
    ]

    with patch("podforge_research_mcp.tools.news.NewsApiClient") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.get_everything.return_value = {"articles": mock_articles}
        mock_cls.return_value = mock_instance

        articles = await news.get_news_today("technology")

    assert len(articles) == 1
    assert articles[0]["title"] == "Breaking News"
