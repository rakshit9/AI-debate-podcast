"""Fact-check chain — extract claims and verify against research."""

import json
from pathlib import Path
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from ..config import get_settings
from ..graphs.state import ScriptLine
from ..llm import get_llm

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "pipeline" / "fact_checker_v1.md"


class Claim(BaseModel):
    line_index: int = Field(description="Index of the script line containing this claim")
    speaker: str
    text: str = Field(description="The specific claim text")
    verified: bool = Field(description="Whether claim is supported by research")
    confidence: float = Field(ge=0.0, le=1.0)
    correction: str | None = Field(default=None, description="Suggested correction if wrong")


class FactCheckResult(BaseModel):
    claims: list[Claim]
    overall_accuracy: float = Field(ge=0.0, le=1.0)
    needs_correction: bool
    flagged_lines: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of {line_index, correction} for flagged lines",
    )


async def run_fact_check_chain(
    script: list[ScriptLine],
    research_data: dict[str, Any],
) -> dict[str, Any]:
    """Verify factual claims in the script. Returns FactCheckResult as dict."""
    if not script:
        return FactCheckResult(
            claims=[], overall_accuracy=1.0, needs_correction=False, flagged_lines=[]
        ).model_dump()

    settings = get_settings()
    llm = get_llm(model=settings.fact_check_model or None)
    structured_llm = llm.with_structured_output(FactCheckResult)

    system_prompt = _PROMPT_PATH.read_text()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "human",
                "Script (JSON):\n{script}\n\nResearch sources:\n{sources}",
            ),
        ]
    )
    chain = prompt | structured_llm

    # Only send first 10 lines + relevant research to keep context tight
    script_subset = [
        {"index": i, "speaker": line["speaker"], "text": line["text"]}
        for i, line in enumerate(script[:20])
    ]
    sources = json.dumps(
        {
            "web": [
                r.get("title", "") + ": " + r.get("content", "")[:200]
                for r in research_data.get("web", [])[:5]
            ],
        }
    )
    result: FactCheckResult = await chain.ainvoke(  # type: ignore[assignment]
        {"script": json.dumps(script_subset), "sources": sources}
    )

    # Populate flagged_lines from claims
    flagged = [
        {"line_index": c.line_index, "correction": c.correction}
        for c in result.claims
        if not c.verified and c.correction
    ]
    result.flagged_lines = flagged
    result.needs_correction = len(flagged) > 0

    return result.model_dump()
