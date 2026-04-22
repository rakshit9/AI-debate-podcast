import asyncio
from typing import Any

import httpx

from ..config import get_settings


def _upload_youtube_sync(audio_url: str, metadata: dict[str, Any]) -> str:
    """Upload to YouTube via Data API v3 resumable upload.

    Requires oauth_token with youtube.upload scope stored in settings.
    Returns the YouTube video URL.
    """
    settings = get_settings()

    # Download audio file first
    with httpx.Client(timeout=120) as http:
        r = http.get(audio_url)
        r.raise_for_status()
        audio_bytes = r.content

    headers = {
        "Authorization": f"Bearer {settings.youtube_oauth_token}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "snippet": {
            "title": str(metadata.get("title", "PodForge Episode")),
            "description": str(metadata.get("description", "")),
            "tags": metadata.get("tags", []),
            "categoryId": "22",
        },
        "status": {"privacyStatus": metadata.get("privacy", "public")},
    }

    # Initiate resumable upload
    init_resp = httpx.post(
        "https://www.googleapis.com/upload/youtube/v3/videos"
        "?uploadType=resumable&part=snippet,status",
        headers=headers,
        json=body,
    )
    init_resp.raise_for_status()
    upload_url: str = init_resp.headers["Location"]

    # Upload bytes
    upload_resp = httpx.put(
        upload_url,
        content=audio_bytes,
        headers={"Content-Type": "audio/mpeg"},
        timeout=300,
    )
    upload_resp.raise_for_status()
    data: dict[str, Any] = upload_resp.json()
    video_id: str = str(data.get("id", ""))
    return f"https://www.youtube.com/watch?v={video_id}"


async def publish_youtube(audio_url: str, metadata: dict[str, Any]) -> str:
    """Upload an audio file to YouTube as a video. Returns the YouTube URL."""
    return await asyncio.to_thread(_upload_youtube_sync, audio_url, metadata)
