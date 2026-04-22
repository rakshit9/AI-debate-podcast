from typing import Any

from ..graphs.state import PipelineState
from ..mcp_clients import publish as publish_client


async def publish_node(state: PipelineState) -> dict[str, Any]:
    """Upload to S3 and generate RSS item via publish-mcp."""
    audio_url = state.get("final_audio_url") or ""
    if not audio_url:
        return {"errors": state["errors"] + ["No audio to publish"]}

    episode_data: dict[str, Any] = {
        "id": state["episode_id"],
        "show_id": state["show_id"],
        "topic": state["topic"],
        "audio_url": audio_url,
        "description": f"AI-generated debate on: {state['topic']}",
    }

    rss_xml = await publish_client.generate_rss_item(episode_data)

    published_urls: dict[str, str] = {
        "audio": audio_url,
        "rss": f"data:application/rss+xml,{rss_xml[:200]}",
    }

    return {"published_urls": published_urls}
