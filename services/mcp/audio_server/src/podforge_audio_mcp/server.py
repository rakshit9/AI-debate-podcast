from typing import Any

from mcp.server.fastmcp import FastMCP

from .tools.mixer import (
    add_intro_outro,
    apply_compression,
    generate_waveform,
    mix_tracks,
)
from .tools.transcribe import transcribe_audio
from .tools.tts import text_to_speech as _text_to_speech

mcp: FastMCP = FastMCP("podforge-audio-mcp")


@mcp.tool()
async def tts(
    text: str,
    voice_id: str,
    provider: str = "elevenlabs",
) -> dict[str, Any]:
    """Convert text to speech. Returns audio_url, duration_seconds, provider."""
    return await _text_to_speech(text, voice_id, provider)


@mcp.tool()
async def mix(segment_urls: list[str], crossfade_ms: int = 200) -> dict[str, Any]:
    """Mix multiple audio segment URLs with crossfade. Returns audio_url + duration."""
    return await mix_tracks(segment_urls, crossfade_ms)


@mcp.tool()
async def bookend(
    audio_url: str,
    intro_url: str | None = None,
    outro_url: str | None = None,
) -> dict[str, Any]:
    """Add intro and/or outro clips to an audio file."""
    return await add_intro_outro(audio_url, intro_url, outro_url)


@mcp.tool()
async def compress(
    audio_url: str,
    threshold_dbfs: float = -20.0,
    ratio: float = 4.0,
) -> dict[str, Any]:
    """Apply dynamic range compression to audio. Returns audio_url."""
    return await apply_compression(audio_url, threshold_dbfs, ratio)


@mcp.tool()
async def waveform(audio_url: str) -> str:
    """Generate an SVG waveform visualization from an audio URL."""
    return await generate_waveform(audio_url)


@mcp.tool()
async def transcribe(audio_url: str) -> str:
    """Transcribe audio to text via OpenAI Whisper."""
    return await transcribe_audio(audio_url)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
