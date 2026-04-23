import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from ..config import get_settings
from ..graphs.state import PipelineState
from ..llm import get_llm


async def quality_gate_node(state: PipelineState) -> dict[str, Any]:
    """LLM-judge the outline quality. Approve or flag for retry."""
    settings = get_settings()
    llm = get_llm(model=settings.outline_model or None)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a podcast quality reviewer. Rate the following episode outline "
                "on a scale of 1-10 for debate potential, clarity, and audience interest. "
                'Respond ONLY with JSON: {"score": <int>, "reason": "<str>"}',
            ),
            ("human", "Topic: {topic}\n\nOutline:\n{outline}"),
        ]
    )
    response = await (prompt | llm).ainvoke(
        {"topic": state["topic"], "outline": json.dumps(state["outline"], indent=2)}
    )

    try:
        data: dict[str, Any] = json.loads(str(response.content))
        score = float(data.get("score", 0))
        reason = str(data.get("reason", ""))
    except (json.JSONDecodeError, ValueError):
        score = 5.0
        reason = "Could not parse quality score."

    passed = (
        score >= settings.quality_threshold or state["retry_count"] >= settings.max_outline_retries
    )

    errors = list(state["errors"])
    if not passed:
        errors.append(f"Outline quality {score:.0f}/10 — {reason}. Retrying.")

    return {
        "outline_approved": passed,
        "retry_count": state["retry_count"] + (0 if passed else 1),
        "errors": errors,
    }


def quality_gate_router(state: PipelineState) -> str:
    return "debate" if state["outline_approved"] else "outline"
