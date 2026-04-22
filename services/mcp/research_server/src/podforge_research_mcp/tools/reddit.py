import asyncio
from typing import Any

import praw

from ..config import get_settings


def _get_reddit_sync(subreddit: str, topic: str, limit: int) -> list[dict[str, Any]]:
    settings = get_settings()
    reddit = praw.Reddit(
        client_id=settings.reddit_client_id,
        client_secret=settings.reddit_client_secret,
        user_agent=settings.reddit_user_agent,
    )
    sub = reddit.subreddit(subreddit)
    results: list[dict[str, Any]] = []
    for submission in sub.search(topic, limit=limit, sort="relevance"):
        results.append(
            {
                "title": submission.title,
                "url": f"https://reddit.com{submission.permalink}",
                "score": submission.score,
                "num_comments": submission.num_comments,
                "text": submission.selftext[:2000] if submission.selftext else "",
                "created_utc": submission.created_utc,
            }
        )
    return results


async def get_reddit_threads(subreddit: str, topic: str, limit: int = 10) -> list[dict[str, Any]]:
    """Fetch relevant Reddit threads from a subreddit for a topic."""
    return await asyncio.to_thread(_get_reddit_sync, subreddit, topic, limit)
