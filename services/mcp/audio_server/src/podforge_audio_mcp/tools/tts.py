import asyncio
import io
from typing import Any

from pydub import AudioSegment

from ..config import get_settings
from .storage import upload_audio


def _tts_elevenlabs_sync(text: str, voice_id: str, api_key: str) -> bytes:
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)
    # text_to_speech.convert returns a generator of bytes chunks
    audio_gen = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_turbo_v2",
    )
    return b"".join(audio_gen)


async def text_to_speech(
    text: str,
    voice_id: str,
    provider: str = "elevenlabs",
) -> dict[str, Any]:
    """Convert text to speech. Returns audio_url, duration_seconds, provider."""
    settings = get_settings()

    if provider == "elevenlabs":
        audio_bytes = await asyncio.to_thread(
            _tts_elevenlabs_sync, text, voice_id, settings.elevenlabs_api_key
        )
    else:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text,
        )
        audio_bytes = response.content

    audio_url = await upload_audio(audio_bytes, prefix="tts")

    seg: AudioSegment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    duration_seconds = len(seg) / 1000.0

    return {
        "audio_url": audio_url,
        "duration_seconds": duration_seconds,
        "provider": provider,
    }
