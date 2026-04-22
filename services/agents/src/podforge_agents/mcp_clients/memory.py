"""Memory MCP client — wraps podforge-memory-mcp tool functions."""

from typing import Any

from podforge_memory_mcp.tools.metadata import get_host_profile, get_show_style_guide
from podforge_memory_mcp.tools.vectors import (
    get_host_memory,
    index_episode,
    search_past_episodes,
    update_host_memory,
)

__all__ = [
    "get_host_memory",
    "update_host_memory",
    "search_past_episodes",
    "index_episode",
    "get_show_style_guide",
    "host_profile",
]


async def host_profile(host_id: str) -> dict[str, Any]:
    """Fetch host profile by name or UUID."""
    result: dict[str, Any] = await get_host_profile(host_id)
    return result
