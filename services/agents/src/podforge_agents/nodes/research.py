import asyncio
from typing import Any

from ..graphs.state import PipelineState
from ..mcp_clients import research as research_client


async def research_node(state: PipelineState) -> dict[str, Any]:
    """Fan out to all research sources in parallel via research-mcp."""
    topic = state["topic"]

    results: tuple[Any, ...] = await asyncio.gather(
        research_client.search_web(topic, num_results=10),
        research_client.fetch_arxiv(topic, max_papers=5),
        research_client.get_news_today(topic, page_size=10),
        return_exceptions=True,
    )
    web, arxiv, news = results

    return {
        "research_data": {
            **state.get("research_data", {}),
            "web": web if not isinstance(web, BaseException) else [],
            "arxiv": arxiv if not isinstance(arxiv, BaseException) else [],
            "news": news if not isinstance(news, BaseException) else [],
        }
    }
