import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_upload_audio_returns_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("S3_ENDPOINT", "http://localhost:9000")
    monkeypatch.setenv("S3_BUCKET", "podforge")

    with patch("podforge_audio_mcp.tools.storage.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        from podforge_audio_mcp.tools.storage import upload_audio

        url = await upload_audio(b"fake-audio", prefix="tts")

    assert url.startswith("http://localhost:9000/podforge/tts/")
    mock_s3.put_object.assert_called_once()


@pytest.mark.asyncio
async def test_transcribe_audio_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    mock_transcript = MagicMock()
    mock_transcript.text = "Hello world"

    with (
        patch("podforge_audio_mcp.tools.transcribe.httpx.AsyncClient") as mock_http_cls,
        patch("podforge_audio_mcp.tools.transcribe.AsyncOpenAI") as mock_oai_cls,
    ):
        mock_http = AsyncMock()
        mock_http_response = MagicMock()
        mock_http_response.content = b"audio"
        mock_http_response.raise_for_status = MagicMock()
        mock_http.get.return_value = mock_http_response
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)
        mock_http_cls.return_value = mock_http

        mock_oai = AsyncMock()
        mock_oai.audio.transcriptions.create.return_value = mock_transcript
        mock_oai_cls.return_value = mock_oai

        from podforge_audio_mcp.tools.transcribe import transcribe_audio

        text = await transcribe_audio("http://localhost:9000/audio.mp3")

    assert text == "Hello world"


@pytest.mark.asyncio
async def test_generate_waveform_returns_svg() -> None:
    # Build a minimal valid MP3-like fixture using pydub silence
    from pydub.generators import Sine

    sine = Sine(440).to_audio_segment(duration=1000)
    buf = io.BytesIO()
    sine.export(buf, format="mp3")
    mp3_bytes = buf.getvalue()

    with patch("podforge_audio_mcp.tools.mixer._download_audio", new_callable=AsyncMock) as mock_dl:
        mock_dl.return_value = mp3_bytes

        from podforge_audio_mcp.tools.mixer import generate_waveform

        svg = await generate_waveform("http://localhost:9000/audio.mp3")

    assert svg.startswith("<svg")
    assert "line" in svg
