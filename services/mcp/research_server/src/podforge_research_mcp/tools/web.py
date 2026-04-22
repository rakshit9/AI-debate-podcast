import json
from typing import Any

import redis.asyncio as aioredis
from tavily import AsyncTavilyClient

from ..config import get_settings


async def search_web(query: str, num_results: int = 10) -> list[dict[str, Any]]:
    """Search the web using Tavily. Results cached in Redis for 1 hour."""
    settings = get_settings()
    cache_key = f"research:web:{query}:{num_results}"

    async with aioredis.from_url(settings.redis_url) as r:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)  # type: ignore[no-any-return]

    client = AsyncTavilyClient(api_key=settings.tavily_api_key)
    response: dict[str, Any] = await client.search(query=query, max_results=num_results)
    results: list[dict[str, Any]] = response.get("results", [])

    async with aioredis.from_url(settings.redis_url) as r:
        await r.setex(cache_key, settings.cache_ttl_seconds, json.dumps(results))

    return results
