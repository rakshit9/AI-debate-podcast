import asyncio
from typing import Any

import tweepy

from ..config import get_settings


def _tweet_sync(text: str) -> str:
    settings = get_settings()
    client = tweepy.Client(
        bearer_token=settings.twitter_bearer_token,
        consumer_key=settings.twitter_api_key,
        consumer_secret=settings.twitter_api_secret,
        access_token=settings.twitter_access_token,
        access_token_secret=settings.twitter_access_secret,
    )
    response = client.create_tweet(text=text)
    tweet_id: str = str(response.data["id"])
    return f"https://twitter.com/i/web/status/{tweet_id}"


async def tweet_episode(episode_data: dict[str, Any]) -> str:
    """Tweet a new episode announcement. Returns the tweet URL."""
    topic = str(episode_data.get("topic", "New Episode"))
    audio_url = str(episode_data.get("audio_url", ""))
    text = f"🎙️ New PodForge episode: {topic}\n\n{audio_url}"[:280]
    return await asyncio.to_thread(_tweet_sync, text)
