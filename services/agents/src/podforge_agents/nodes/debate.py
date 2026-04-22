from typing import Any

from ..debates.debate_format import run_debate
from ..graphs.state import PipelineState, ScriptLine


async def debate_node(state: PipelineState) -> dict[str, Any]:
    """Run the AutoGen SelectorGroupChat debate to produce the episode script."""
    script: list[ScriptLine] = await run_debate(
        topic=state["topic"],
        outline=state["outline"],
        research_data=state["research_data"],
        fmt=state["format"],
    )

    transcript = "\n".join(f"[{line['speaker']}] {line['text']}" for line in script)

    return {
        "script": script,
        "transcript": transcript,
    }
