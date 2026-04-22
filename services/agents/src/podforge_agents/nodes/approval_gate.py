from typing import Any

from langgraph.types import interrupt

from ..graphs.state import PipelineState


async def approval_gate_node(state: PipelineState) -> dict[str, Any]:
    """Optional human-in-the-loop checkpoint before publishing."""
    if not state.get("requires_human_approval", False):
        return {}

    decision: str = interrupt(
        {
            "message": "Episode ready for review. Approve to publish.",
            "audio_url": state.get("final_audio_url"),
            "transcript": state.get("transcript"),
        }
    )

    if decision != "approve":
        return {
            "errors": state["errors"] + [f"Episode rejected by reviewer: {decision}"],
            "published_urls": {},
        }

    return {}


def approval_gate_router(state: PipelineState) -> str:
    if state["errors"] and any("rejected" in e for e in state["errors"]):
        return "__end__"
    return "publish"
