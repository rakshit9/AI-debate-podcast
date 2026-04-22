from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_generate_intro_music_returns_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIXABAY_API_KEY", "test-key")

    mock_hit = {"audio": {"url": "https://cdn.pixabay.com/audio/upbeat.mp3"}, "pageURL": ""}
    mock_response = MagicMock()
    mock_response.json.return_value = {"hits": [mock_hit]}
    mock_response.raise_for_status = MagicMock()

    with patch("podforge_music_mcp.tools.pixabay.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        from podforge_music_mcp.tools.pixabay import generate_intro_music

        url = await generate_intro_music("upbeat")

    assert url == "https://cdn.pixabay.com/audio/upbeat.mp3"


@pytest.mark.asyncio
async def test_generate_intro_music_returns_empty_on_no_hits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PIXABAY_API_KEY", "test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {"hits": []}
    mock_response.raise_for_status = MagicMock()

    with patch("podforge_music_mcp.tools.pixabay.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_client

        from podforge_music_mcp.tools.pixabay import generate_intro_music

        url = await generate_intro_music("unknown_mood")

    assert url == ""


@pytest.mark.asyncio
async def test_match_music_to_mood_selects_upbeat(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIXABAY_API_KEY", "test-key")

    with patch(
        "podforge_music_mcp.tools.pixabay.generate_intro_music",
        new_callable=AsyncMock,
        return_value="https://music.example.com/upbeat.mp3",
    ) as mock_gen:
        from podforge_music_mcp.tools.pixabay import match_music_to_mood

        url = await match_music_to_mood("This is an amazing and exciting breakthrough!")

    mock_gen.assert_called_once_with("upbeat")
    assert url == "https://music.example.com/upbeat.mp3"
