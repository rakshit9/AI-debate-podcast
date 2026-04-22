import asyncio
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled


def _fetch_transcripts_sync(video_ids: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for vid_id in video_ids:
        try:
            segments: list[dict[str, Any]] = YouTubeTranscriptApi.get_transcript(vid_id)  # type: ignore[attr-defined]
            full_text = " ".join(seg["text"] for seg in segments)
            results.append({"video_id": vid_id, "transcript": full_text, "error": None})
        except TranscriptsDisabled:
            results.append({"video_id": vid_id, "transcript": "", "error": "transcripts_disabled"})
        except Exception as exc:
            results.append({"video_id": vid_id, "transcript": "", "error": str(exc)})
    return results


async def fetch_youtube_transcripts(video_ids: list[str]) -> list[dict[str, Any]]:
    """Fetch transcripts for a list of YouTube video IDs."""
    return await asyncio.to_thread(_fetch_transcripts_sync, video_ids)
