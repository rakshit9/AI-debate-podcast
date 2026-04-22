from typing import Any

import httpx

from ..config import get_settings

_MOOD_QUERIES: dict[str, str] = {
    "upbeat": "upbeat podcast intro energetic",
    "calm": "calm ambient background",
    "dramatic": "dramatic cinematic tension",
    "tech": "electronic technology background",
    "news": "news broadcast background",
    "comedy": "fun playful background music",
}

_SFX_QUERIES: dict[str, str] = {
    "transition": "whoosh transition sound",
    "applause": "crowd applause",
    "bell": "notification bell",
    "typing": "keyboard typing",
    "intro_sting": "podcast intro sting",
}


async def _search_pixabay(query: str, media_type: str = "music") -> list[dict[str, Any]]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            settings.pixabay_base_url,
            params={
                "key": settings.pixabay_api_key,
                "q": query,
                "media_type": media_type,
                "per_page": 5,
            },
        )
        r.raise_for_status()
        data: dict[str, Any] = r.json()
    hits: list[dict[str, Any]] = data.get("hits", [])
    return hits


async def generate_intro_music(mood: str, duration_sec: int = 30) -> str:
    """Return a Pixabay music URL matching the requested mood."""
    query = _MOOD_QUERIES.get(mood, f"{mood} background music podcast")
    hits = await _search_pixabay(query)
    if not hits:
        return ""
    # Return the first available audio URL
    hit: dict[str, Any] = hits[0]
    audio_url: str = str(
        hit.get("audio", {}).get("url", "") or hit.get("webformatURL", "") or hit.get("pageURL", "")
    )
    return audio_url


async def get_transition_sfx(sfx_type: str) -> str:
    """Return a Pixabay SFX URL for the requested transition type."""
    query = _SFX_QUERIES.get(sfx_type, f"{sfx_type} sound effect")
    hits = await _search_pixabay(query, media_type="music")
    if not hits:
        return ""
    hit: dict[str, Any] = hits[0]
    return str(hit.get("audio", {}).get("url", "") or hit.get("pageURL", ""))


async def match_music_to_mood(script_section: str) -> str:
    """Pick background music URL based on the emotional tone of a script section."""
    section_lower = script_section.lower()
    if any(w in section_lower for w in ["exciting", "amazing", "breakthrough", "incredible"]):
        mood = "upbeat"
    elif any(w in section_lower for w in ["serious", "warning", "critical", "danger"]):
        mood = "dramatic"
    elif any(w in section_lower for w in ["technology", "AI", "software", "data"]):
        mood = "tech"
    elif any(w in section_lower for w in ["news", "report", "update", "announcement"]):
        mood = "news"
    else:
        mood = "calm"
    return await generate_intro_music(mood)
