import asyncio
from typing import Any

from newsapi import NewsApiClient

from ..config import get_settings


def _fetch_news_sync(topic: str, page_size: int) -> list[dict[str, Any]]:
    settings = get_settings()
    client = NewsApiClient(api_key=settings.newsapi_key)
    response: dict[str, Any] = client.get_everything(
        q=topic,
        language="en",
        sort_by="publishedAt",
        page_size=page_size,
    )
    articles: list[dict[str, Any]] = response.get("articles", [])
    return [
        {
            "title": a.get("title", ""),
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
            "description": a.get("description", ""),
            "published_at": a.get("publishedAt", ""),
        }
        for a in articles
    ]


async def get_news_today(topic: str, page_size: int = 10) -> list[dict[str, Any]]:
    """Fetch today's news articles for a topic via NewsAPI."""
    return await asyncio.to_thread(_fetch_news_sync, topic, page_size)
