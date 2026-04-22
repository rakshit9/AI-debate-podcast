import asyncio
from datetime import UTC, datetime
from typing import Any

from feedgen.feed import FeedGenerator


def _build_rss_item_sync(episode: dict[str, Any], base_url: str) -> str:
    fg = FeedGenerator()
    fg.load_extension("podcast")

    show_title = str(episode.get("show_title", "PodForge Show"))
    fg.title(show_title)
    fg.link(href=base_url)
    fg.language("en")
    fg.description(str(episode.get("show_description", show_title)))

    fe = fg.add_entry()
    fe.id(str(episode.get("id", "")))
    fe.title(str(episode.get("topic", "Episode")))
    fe.description(str(episode.get("description", "")))
    pub_date = episode.get("published_at")
    if isinstance(pub_date, str):
        fe.published(pub_date)
    else:
        fe.published(datetime.now(tz=UTC).isoformat())

    audio_url = str(episode.get("audio_url", ""))
    if audio_url:
        fe.enclosure(audio_url, "0", "audio/mpeg")

    rss_bytes: bytes = fg.rss_str(pretty=True)
    return rss_bytes.decode("utf-8")


async def generate_rss_item(episode: dict[str, Any], base_url: str = "") -> str:
    """Generate an RSS 2.0 feed item XML string for a podcast episode."""
    from ..config import get_settings

    settings = get_settings()
    resolved_base = base_url or settings.rss_base_url
    return await asyncio.to_thread(_build_rss_item_sync, episode, resolved_base)
