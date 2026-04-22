import io

import httpx


async def transcribe_audio(audio_url: str) -> str:
    """Transcribe audio from a URL using OpenAI Whisper."""
    from openai import AsyncOpenAI

    from ..config import get_settings

    settings = get_settings()

    async with httpx.AsyncClient(timeout=120) as http:
        r = await http.get(audio_url)
        r.raise_for_status()
        audio_bytes = r.content

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.mp3"

    transcript = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )
    return transcript.text
