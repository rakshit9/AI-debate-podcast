"""Music MCP client — wraps podforge-music-mcp tool functions."""

from podforge_music_mcp.tools.pixabay import (
    generate_intro_music,
    get_transition_sfx,
    match_music_to_mood,
)


async def intro_music(mood: str, duration_sec: int = 30) -> str:
    return str(await generate_intro_music(mood, duration_sec))


async def transition_sfx(sfx_type: str) -> str:
    return str(await get_transition_sfx(sfx_type))


async def mood_music(script_section: str) -> str:
    return str(await match_music_to_mood(script_section))


__all__ = ["intro_music", "transition_sfx", "mood_music"]
