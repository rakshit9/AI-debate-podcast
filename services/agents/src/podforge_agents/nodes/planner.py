from pathlib import Path
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from ..config import get_settings
from ..graphs.state import PipelineState

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "pipeline" / "planner_v1.md"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text()


async def planner_node(state: PipelineState) -> dict[str, Any]:
    """Scope the topic, pick a debate angle, identify key positions."""
    settings = get_settings()
    llm = ChatAnthropic(
        model=settings.planner_model,
        api_key=settings.anthropic_api_key,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _load_prompt()),
            ("human", "Topic: {topic}\nFormat: {format}"),
        ]
    )
    chain = prompt | llm
    response = await chain.ainvoke({"topic": state["topic"], "format": state["format"]})
    plan_text = str(response.content)

    return {
        "research_data": {
            **state.get("research_data", {}),
            "plan": plan_text,
        }
    }
