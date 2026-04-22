from mcp.server.fastmcp import FastMCP

from .tools.pixabay import generate_intro_music, get_transition_sfx, match_music_to_mood

mcp: FastMCP = FastMCP("podforge-music-mcp")


@mcp.tool()
async def intro_music(mood: str, duration_sec: int = 30) -> str:
    """Return a Pixabay music URL matching the requested mood.

    Supported moods: upbeat, calm, dramatic, tech, news, comedy.
    """
    return await generate_intro_music(mood, duration_sec)


@mcp.tool()
async def transition_sfx(sfx_type: str) -> str:
    """Return a Pixabay SFX URL for a transition type.

    Supported types: transition, applause, bell, typing, intro_sting.
    """
    return await get_transition_sfx(sfx_type)


@mcp.tool()
async def mood_music(script_section: str) -> str:
    """Detect emotional tone in a script section and return matching music URL."""
    return await match_music_to_mood(script_section)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
