import asyncio
from typing import Any

from ..graphs.state import PipelineState
from ..mcp_clients import audio as audio_client
from ..mcp_clients import memory as memory_client

# Fallback voice IDs if host profiles aren't in DB yet
_DEFAULT_VOICES: dict[str, tuple[str, str]] = {
    "DrSkeptic": ("pNInz6obpgDQGcFmaJgB", "elevenlabs"),
    "TheOptimist": ("EXAVITQu4vr4xnSDxMaL", "elevenlabs"),
    "Moderator": ("21m00Tcm4TlvDq8ikWAM", "elevenlabs"),
}


async def _resolve_voice(speaker: str, show_id: str) -> tuple[str, str]:
    try:
        profile = await memory_client.host_profile(speaker)
        if profile.get("voice_id"):
            return str(profile["voice_id"]), str(profile.get("voice_provider", "elevenlabs"))
    except Exception:  # noqa: S110
        pass
    return _DEFAULT_VOICES.get(speaker, ("21m00Tcm4TlvDq8ikWAM", "elevenlabs"))


async def tts_node(state: PipelineState) -> dict[str, Any]:
    """Generate TTS audio for each script line in parallel via audio-mcp."""
    script = state["script"]
    show_id = state["show_id"]

    voice_cache: dict[str, tuple[str, str]] = {}
    for line in script:
        speaker = line["speaker"]
        if speaker not in voice_cache:
            voice_cache[speaker] = await _resolve_voice(speaker, show_id)

    tasks = [
        audio_client.text_to_speech(
            text=line["text"],
            voice_id=voice_cache[line["speaker"]][0],
            provider=voice_cache[line["speaker"]][1],
        )
        for line in script
    ]
    segments: list[Any] = list(await asyncio.gather(*tasks, return_exceptions=True))

    # Replace exceptions with empty placeholders
    audio_segments: list[dict[str, Any]] = [
        seg
        if isinstance(seg, dict)
        else {"audio_url": "", "duration_seconds": 0.0, "error": str(seg)}
        for seg in segments
    ]

    return {"audio_segments": audio_segments}
