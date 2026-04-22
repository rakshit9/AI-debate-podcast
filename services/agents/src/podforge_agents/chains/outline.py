"""Outline chain — structured episode blueprint with Pydantic output."""

from pathlib import Path
from typing import Any, Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from ..config import get_settings
from .research import summarise_research

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "pipeline" / "outline_v1.md"


class OutlinePoint(BaseModel):
    title: str = Field(description="Section title")
    key_arguments: list[str] = Field(description="2-3 key arguments for this point")
    supporting_evidence: list[str] = Field(description="Evidence from research")
    estimated_minutes: int = Field(default=3, description="Estimated airtime in minutes")


class EpisodeOutline(BaseModel):
    intro: str = Field(description="Episode introduction (1-2 sentences the Moderator reads)")
    points: list[OutlinePoint] = Field(description="3-5 main discussion points")
    conclusion: str = Field(description="Closing summary and call to action")
    estimated_duration_min: int = Field(description="Total estimated episode duration")
    debate_stance_a: str = Field(description="The skeptic's core position")
    debate_stance_b: str = Field(description="The optimist's core position")


async def run_outline_chain(
    topic: str,
    research_data: dict[str, Any],
    fmt: Literal["debate", "interview", "panel"] = "debate",
) -> dict[str, Any]:
    """Generate and return a structured episode outline."""
    settings = get_settings()
    llm = ChatAnthropic(
        model=settings.outline_model,
        api_key=settings.anthropic_api_key,
    )
    structured_llm = llm.with_structured_output(EpisodeOutline)

    system_prompt = _PROMPT_PATH.read_text()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Topic: {topic}\nFormat: {format}\nResearch digest:\n{digest}"),
        ]
    )
    digest = await summarise_research(topic, research_data)
    chain = prompt | structured_llm
    outline: EpisodeOutline = await chain.ainvoke(  # type: ignore[assignment]
        {"topic": topic, "format": fmt, "digest": digest}
    )
    return outline.model_dump()
