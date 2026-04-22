from typing import Any

from ..graphs.state import PipelineState
from ..mcp_clients import audio as audio_client
from ..mcp_clients import music as music_client


async def mix_node(state: PipelineState) -> dict[str, Any]:
    """Mix TTS segments, add intro/outro music, upload final episode."""
    segment_urls = [seg["audio_url"] for seg in state["audio_segments"] if seg.get("audio_url")]

    if not segment_urls:
        return {
            "errors": state["errors"] + ["No audio segments to mix"],
            "final_audio_url": None,
        }

    # Mix all spoken segments
    mixed = await audio_client.mix_tracks(segment_urls, crossfade_ms=150)

    # Fetch intro/outro music based on show mood
    intro_url = await music_client.intro_music("upbeat", duration_sec=15)
    outro_url = await music_client.intro_music("calm", duration_sec=10)

    # Add bookends
    bookend_result = await audio_client.add_intro_outro(
        audio_url=mixed["audio_url"],
        intro_url=intro_url or None,
        outro_url=outro_url or None,
    )

    # Apply mastering compression
    final = await audio_client.apply_compression(
        audio_url=bookend_result["audio_url"],
        threshold_dbfs=-18.0,
        ratio=3.5,
    )

    return {"final_audio_url": final["audio_url"]}
