from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_upload_s3_returns_url(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    monkeypatch.setenv("S3_ENDPOINT", "http://localhost:9000")
    monkeypatch.setenv("S3_BUCKET", "podforge")

    test_file = tmp_path / "episode.mp3"
    test_file.write_bytes(b"fake audio")

    with patch("podforge_publish_mcp.tools.s3.boto3.client") as mock_boto:
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3

        from podforge_publish_mcp.tools.s3 import upload_s3

        url = await upload_s3(str(test_file))

    assert url.startswith("http://localhost:9000/podforge/episodes/")
    mock_s3.upload_file.assert_called_once()


@pytest.mark.asyncio
async def test_generate_rss_item_returns_xml() -> None:
    episode: dict[str, Any] = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "topic": "AI vs Human Creativity",
        "show_title": "The Forge Podcast",
        "show_description": "Daily AI debates",
        "audio_url": "http://localhost:9000/podforge/episodes/test.mp3",
        "description": "A deep dive",
        "published_at": "2024-01-01T00:00:00+00:00",
    }

    from podforge_publish_mcp.tools.rss import generate_rss_item

    xml = await generate_rss_item(episode, "http://localhost:8000")

    assert "AI vs Human Creativity" in xml
    assert "<rss" in xml


@pytest.mark.asyncio
async def test_tweet_episode_returns_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TWITTER_BEARER_TOKEN", "test")
    monkeypatch.setenv("TWITTER_API_KEY", "test")
    monkeypatch.setenv("TWITTER_API_SECRET", "test")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "test")
    monkeypatch.setenv("TWITTER_ACCESS_SECRET", "test")

    mock_response = MagicMock()
    mock_response.data = {"id": "1234567890"}

    with patch("podforge_publish_mcp.tools.twitter.tweepy.Client") as mock_cls:
        mock_client = MagicMock()
        mock_client.create_tweet.return_value = mock_response
        mock_cls.return_value = mock_client

        from podforge_publish_mcp.tools.twitter import tweet_episode

        url = await tweet_episode({"topic": "Test Episode", "audio_url": "http://example.com"})

    assert "1234567890" in url
