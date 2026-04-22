from typing import Any

from ..chains.fact_check import run_fact_check_chain
from ..graphs.state import PipelineState


async def fact_check_node(state: PipelineState) -> dict[str, Any]:
    """Extract and verify factual claims in the script against research."""
    results = await run_fact_check_chain(
        script=state["script"],
        research_data=state["research_data"],
    )
    return {
        "fact_check_results": results,
        "script_clean": not results.get("needs_correction", False),
    }


def fact_check_router(state: PipelineState) -> str:
    return "tts" if state["script_clean"] else "correction"
