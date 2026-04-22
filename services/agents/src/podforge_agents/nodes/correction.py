import json
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from ..config import get_settings
from ..graphs.state import PipelineState, ScriptLine


async def correction_node(state: PipelineState) -> dict[str, Any]:
    """Rewrite script lines flagged by fact-check."""
    settings = get_settings()
    fact_results = state["fact_check_results"]
    flagged: list[dict[str, Any]] = fact_results.get("flagged_lines", [])

    if not flagged:
        return {"script_clean": True}

    llm = ChatAnthropic(
        model=settings.fact_check_model,
        api_key=settings.anthropic_api_key,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a podcast script editor. Rewrite the provided line to fix the "
                "factual issue described. Keep the speaker's voice and tone. "
                'Return ONLY JSON: {"corrected_text": "<str>"}',
            ),
            (
                "human",
                "Speaker: {speaker}\nOriginal: {text}\nIssue: {issue}\nSupporting facts: {facts}",
            ),
        ]
    )

    script = list(state["script"])
    flagged_indices: dict[int, str] = {
        item["line_index"]: item["correction"] for item in flagged if "line_index" in item
    }

    for idx, correction_hint in flagged_indices.items():
        if idx >= len(script):
            continue
        line = script[idx]
        response = await (prompt | llm).ainvoke(
            {
                "speaker": line["speaker"],
                "text": line["text"],
                "issue": correction_hint,
                "facts": json.dumps(state["research_data"].get("web", [])[:3]),
            }
        )
        try:
            data: dict[str, Any] = json.loads(str(response.content))
            corrected: ScriptLine = {
                "speaker": line["speaker"],
                "text": str(data.get("corrected_text", line["text"])),
            }
            script[idx] = corrected
        except (json.JSONDecodeError, KeyError):
            pass

    return {"script": script, "script_clean": True}
