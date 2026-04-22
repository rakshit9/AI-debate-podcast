from typing import Any

from mcp.server.fastmcp import FastMCP

from .tools import arxiv_tool, news, reader, reddit, youtube
from .tools.web import search_web as _search_web

mcp: FastMCP = FastMCP("podforge-research-mcp")


@mcp.tool()
async def search_web(query: str, num_results: int = 10) -> list[dict[str, Any]]:
    """Search the web for a query using Tavily. Cached in Redis for 1 hour."""
    return await _search_web(query, num_results)


@mcp.tool()
async def fetch_arxiv(topic: str, max_papers: int = 5) -> list[dict[str, Any]]:
    """Fetch academic papers from ArXiv for a topic."""
    return await arxiv_tool.fetch_arxiv(topic, max_papers)


@mcp.tool()
async def get_reddit_threads(subreddit: str, topic: str, limit: int = 10) -> list[dict[str, Any]]:
    """Fetch relevant Reddit threads from a subreddit."""
    return await reddit.get_reddit_threads(subreddit, topic, limit)


@mcp.tool()
async def fetch_youtube_transcripts(video_ids: list[str]) -> list[dict[str, Any]]:
    """Fetch transcripts for YouTube videos by video ID."""
    return await youtube.fetch_youtube_transcripts(video_ids)


@mcp.tool()
async def get_news_today(topic: str, page_size: int = 10) -> list[dict[str, Any]]:
    """Fetch today's news articles for a topic via NewsAPI."""
    return await news.get_news_today(topic, page_size)


@mcp.tool()
async def read_url(url: str) -> str:
    """Fetch and return the text content of a URL."""
    return await reader.read_url(url)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
