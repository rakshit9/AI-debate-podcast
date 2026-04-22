from typing import Any

from ..chains.outline import run_outline_chain
from ..graphs.state import PipelineState


async def outline_node(state: PipelineState) -> dict[str, Any]:
    """Generate a structured episode outline from research data."""
    outline = await run_outline_chain(
        topic=state["topic"],
        research_data=state["research_data"],
        fmt=state["format"],
    )
    return {"outline": outline, "outline_approved": False}
