from typing import Any

from mcp.server.fastmcp import FastMCP

from .tools.metadata import get_host_profile, get_show_style_guide
from .tools.vectors import (
    get_host_memory,
    index_episode,
    search_past_episodes,
    update_host_memory,
)

mcp: FastMCP = FastMCP("podforge-memory-mcp")


@mcp.tool()
async def host_memory_search(host_id: str, query: str, k: int = 5) -> list[dict[str, Any]]:
    """Semantic search over a host's accumulated memories. Returns scored results."""
    return await get_host_memory(host_id, query, k)


@mcp.tool()
async def host_memory_update(host_id: str, content: str) -> None:
    """Append a new memory entry for a host (embedded + stored in Qdrant)."""
    await update_host_memory(host_id, content)


@mcp.tool()
async def episode_search(show_id: str, query: str, k: int = 5) -> list[dict[str, Any]]:
    """Semantic search over past episodes for a show."""
    return await search_past_episodes(show_id, query, k)


@mcp.tool()
async def episode_index(show_id: str, episode_id: str, topic: str, summary: str) -> None:
    """Index a new episode into Qdrant for future semantic search."""
    await index_episode(show_id, episode_id, topic, summary)


@mcp.tool()
async def show_style_guide(show_id: str) -> str:
    """Fetch the style guide for a show from Postgres."""
    return await get_show_style_guide(show_id)


@mcp.tool()
async def host_profile(host_id: str) -> dict[str, Any]:
    """Fetch host name, personality prompt, and voice config from Postgres."""
    return await get_host_profile(host_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
