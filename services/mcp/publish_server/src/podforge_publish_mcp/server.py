from typing import Any

from mcp.server.fastmcp import FastMCP

from .tools.rss import generate_rss_item
from .tools.s3 import upload_s3
from .tools.spotify import publish_spotify
from .tools.twitter import tweet_episode
from .tools.youtube_pub import publish_youtube

mcp: FastMCP = FastMCP("podforge-publish-mcp")


@mcp.tool()
async def s3_upload(file_path: str, bucket: str | None = None) -> str:
    """Upload a local file to S3/MinIO. Returns the public URL."""
    return await upload_s3(file_path, bucket)


@mcp.tool()
async def spotify_publish(episode_data: dict[str, Any]) -> str:
    """Publish episode to Spotify for Podcasters. Returns the show URL."""
    return await publish_spotify(episode_data)


@mcp.tool()
async def youtube_publish(audio_url: str, metadata: dict[str, Any]) -> str:
    """Upload audio to YouTube as a video. Returns the YouTube video URL."""
    return await publish_youtube(audio_url, metadata)


@mcp.tool()
async def rss_item(episode: dict[str, Any], base_url: str = "") -> str:
    """Generate an RSS 2.0 XML item for a podcast episode."""
    return await generate_rss_item(episode, base_url)


@mcp.tool()
async def twitter_post(episode_data: dict[str, Any]) -> str:
    """Tweet a new episode announcement. Returns the tweet URL."""
    return await tweet_episode(episode_data)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
