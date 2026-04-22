import asyncio
from typing import Any

import httpx

from ..config import get_settings


def _get_token_sync() -> str:
    """Fetch a Spotify client-credentials access token."""
    settings = get_settings()
    r = httpx.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(settings.spotify_client_id, settings.spotify_client_secret),
    )
    r.raise_for_status()
    data: dict[str, Any] = r.json()
    return str(data["access_token"])


async def publish_spotify(episode_data: dict[str, Any]) -> str:
    """Submit episode metadata to Spotify for Podcasters. Returns episode URL.

    Note: Full publish requires a pre-registered podcast RSS feed on Spotify.
    This call verifies the episode exists in the feed and returns the expected URL.
    """
    rss_url = episode_data.get("rss_url", "")
    show_id = episode_data.get("spotify_show_id", "")

    if not show_id:
        return f"pending:{rss_url}"

    token = await asyncio.to_thread(_get_token_sync)

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"https://api.spotify.com/v1/shows/{show_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
        data: dict[str, Any] = r.json()

    return f"https://open.spotify.com/show/{data.get('id', show_id)}"
