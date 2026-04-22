from typing import Any

from ..debates.debate_format import run_debate
from ..debates.interview_format import run_interview
from ..debates.panel_format import run_panel
from ..graphs.state import PipelineState, ScriptLine


async def debate_node(state: PipelineState) -> dict[str, Any]:
    """Dispatch to the correct format handler and produce the episode script."""
    fmt = state["format"]
    topic = state["topic"]
    outline = state["outline"]
    research_data = state["research_data"]

    script: list[ScriptLine]
    if fmt == "interview":
        script = await run_interview(topic=topic, outline=outline, research_data=research_data)
    elif fmt == "panel":
        script = await run_panel(topic=topic, outline=outline, research_data=research_data)
    else:
        script = await run_debate(
            topic=topic, outline=outline, research_data=research_data, fmt="debate"
        )

    transcript = "\n".join(f"[{line['speaker']}] {line['text']}" for line in script)
    return {"script": script, "transcript": transcript}
