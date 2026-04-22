from typing import Any

from ..graphs.state import PipelineState
from ..mcp_clients import memory as memory_client


async def memory_update_node(state: PipelineState) -> dict[str, Any]:
    """Index episode + update each host's memory via memory-mcp."""
    # Index episode for future semantic search
    summary = f"Episode on '{state['topic']}'. Format: {state['format']}."
    if state["script"]:
        opening = state["script"][0]["text"][:200]
        summary += f" Opening: {opening}"

    try:
        await memory_client.index_episode(
            show_id=state["show_id"],
            episode_id=state["episode_id"],
            topic=state["topic"],
            summary=summary,
        )
    except Exception:  # noqa: S110
        pass

    # Update each host's memory with what they argued
    speakers: set[str] = {line["speaker"] for line in state["script"]}
    for speaker in speakers:
        lines = [ln["text"] for ln in state["script"] if ln["speaker"] == speaker]
        if lines:
            memory_content = f"Debated '{state['topic']}'. Key argument: {lines[0][:300]}"
            try:
                await memory_client.update_host_memory(speaker, memory_content)
            except Exception:  # noqa: S110
                pass

    return {}
