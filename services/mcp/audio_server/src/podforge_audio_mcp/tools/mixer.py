import asyncio
import io
from typing import Any

import httpx
from pydub import AudioSegment

from .storage import upload_audio


async def _download_audio(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content


def _mix_sync(segment_bytes_list: list[bytes], crossfade_ms: int) -> bytes:
    segments: list[AudioSegment] = [
        AudioSegment.from_file(io.BytesIO(b), format="mp3") for b in segment_bytes_list
    ]
    mixed: AudioSegment = segments[0]
    for seg in segments[1:]:
        mixed = mixed.append(seg, crossfade=crossfade_ms)
    buf = io.BytesIO()
    mixed.export(buf, format="mp3")
    return buf.getvalue()


def _add_bookend_sync(
    main_bytes: bytes, intro_bytes: bytes | None, outro_bytes: bytes | None
) -> bytes:
    main: AudioSegment = AudioSegment.from_file(io.BytesIO(main_bytes), format="mp3")
    if intro_bytes:
        intro: AudioSegment = AudioSegment.from_file(io.BytesIO(intro_bytes), format="mp3")
        main = intro.append(main, crossfade=500)
    if outro_bytes:
        outro: AudioSegment = AudioSegment.from_file(io.BytesIO(outro_bytes), format="mp3")
        main = main.append(outro, crossfade=500)
    buf = io.BytesIO()
    main.export(buf, format="mp3")
    return buf.getvalue()


def _compress_sync(audio_bytes: bytes, threshold_dbfs: float, ratio: float) -> bytes:
    seg: AudioSegment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    # Normalize as a lightweight compression preset
    change_in_dbfs = threshold_dbfs - seg.dBFS
    compressed = seg.apply_gain(change_in_dbfs * (1 - 1 / ratio))
    buf = io.BytesIO()
    compressed.export(buf, format="mp3")
    return buf.getvalue()


def _waveform_sync(audio_bytes: bytes, num_bars: int = 100) -> str:
    seg: AudioSegment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    samples = seg.get_array_of_samples()
    step = max(1, len(samples) // num_bars)
    peak = 1
    buckets: list[float] = []
    for i in range(0, len(samples), step):
        val = abs(int(samples[i]))
        peak = max(peak, val)
        buckets.append(float(val))
    buckets = buckets[:num_bars]
    normalized = [v / peak for v in buckets]

    width, height = 400, 80
    cx = width / len(normalized)
    lines = [
        f'<line x1="{i * cx:.1f}" y1="{40 - v * 38:.1f}" '
        f'x2="{i * cx:.1f}" y2="{40 + v * 38:.1f}" '
        f'stroke="#6366f1" stroke-width="3"/>'
        for i, v in enumerate(normalized)
    ]
    return (
        f'<svg width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg">{"".join(lines)}</svg>'
    )


async def mix_tracks(segment_urls: list[str], crossfade_ms: int = 200) -> dict[str, Any]:
    """Download audio segments by URL, mix with crossfade, upload result."""
    segment_bytes = [await _download_audio(url) for url in segment_urls]
    mixed_bytes = await asyncio.to_thread(_mix_sync, segment_bytes, crossfade_ms)
    audio_url = await upload_audio(mixed_bytes, prefix="mixed")
    seg: AudioSegment = AudioSegment.from_file(io.BytesIO(mixed_bytes), format="mp3")
    return {"audio_url": audio_url, "duration_seconds": len(seg) / 1000.0}


async def add_intro_outro(
    audio_url: str,
    intro_url: str | None = None,
    outro_url: str | None = None,
) -> dict[str, Any]:
    """Add intro and/or outro clips to an audio file."""
    main_bytes = await _download_audio(audio_url)
    intro_bytes = await _download_audio(intro_url) if intro_url else None
    outro_bytes = await _download_audio(outro_url) if outro_url else None
    result_bytes = await asyncio.to_thread(_add_bookend_sync, main_bytes, intro_bytes, outro_bytes)
    url = await upload_audio(result_bytes, prefix="bookend")
    seg: AudioSegment = AudioSegment.from_file(io.BytesIO(result_bytes), format="mp3")
    return {"audio_url": url, "duration_seconds": len(seg) / 1000.0}


async def apply_compression(
    audio_url: str,
    threshold_dbfs: float = -20.0,
    ratio: float = 4.0,
) -> dict[str, Any]:
    """Apply dynamic range compression to audio."""
    audio_bytes = await _download_audio(audio_url)
    compressed = await asyncio.to_thread(_compress_sync, audio_bytes, threshold_dbfs, ratio)
    url = await upload_audio(compressed, prefix="compressed")
    return {"audio_url": url}


async def generate_waveform(audio_url: str) -> str:
    """Generate an SVG waveform visualization from an audio URL."""
    audio_bytes = await _download_audio(audio_url)
    return await asyncio.to_thread(_waveform_sync, audio_bytes)
