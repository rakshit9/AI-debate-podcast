"""Research MCP client — wraps podforge-research-mcp tool functions."""

from podforge_research_mcp.tools.arxiv_tool import fetch_arxiv
from podforge_research_mcp.tools.news import get_news_today
from podforge_research_mcp.tools.reader import read_url
from podforge_research_mcp.tools.reddit import get_reddit_threads
from podforge_research_mcp.tools.web import search_web
from podforge_research_mcp.tools.youtube import fetch_youtube_transcripts

__all__ = [
    "search_web",
    "fetch_arxiv",
    "get_reddit_threads",
    "fetch_youtube_transcripts",
    "get_news_today",
    "read_url",
]
