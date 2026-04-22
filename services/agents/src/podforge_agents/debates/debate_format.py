"""AutoGen SelectorGroupChat debate — the heart of PodForge."""

import json
from pathlib import Path
from typing import Any, Literal

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.anthropic import (
    AnthropicChatCompletionClient,
)

from ..config import get_settings
from ..graphs.state import ScriptLine

_PROMPTS = Path(__file__).parent.parent / "prompts" / "hosts"


def _read(name: str) -> str:
    return (_PROMPTS / name).read_text()


def _make_client(model: str, api_key: str) -> AnthropicChatCompletionClient:
    return AnthropicChatCompletionClient(model=model, api_key=api_key)


def _parse_messages(messages: Any) -> list[ScriptLine]:
    """Convert AutoGen message sequence to structured ScriptLine list."""
    script: list[ScriptLine] = []
    agent_names = {"DrSkeptic", "TheOptimist", "Moderator"}
    for msg in messages:
        source = getattr(msg, "source", None) or getattr(msg, "name", None)
        content = getattr(msg, "content", None)
        if source in agent_names and content:
            text = content if isinstance(content, str) else str(content)
            text = text.strip()
            if text:
                script.append(ScriptLine(speaker=str(source), text=text))
    return script


async def run_debate(
    topic: str,
    outline: dict[str, Any],
    research_data: dict[str, Any],
    fmt: Literal["debate", "interview", "panel"] = "debate",
) -> list[ScriptLine]:
    """Run a 3-agent SelectorGroupChat debate and return the structured script."""
    settings = get_settings()
    model = settings.debate_model
    api_key = settings.anthropic_api_key

    skeptic = AssistantAgent(
        name="DrSkeptic",
        model_client=_make_client(model, api_key),
        system_message=_read("skeptic_v1.md"),
    )
    optimist = AssistantAgent(
        name="TheOptimist",
        model_client=_make_client(model, api_key),
        system_message=_read("optimist_v1.md"),
    )
    moderator = AssistantAgent(
        name="Moderator",
        model_client=_make_client(model, api_key),
        system_message=_read("moderator_v1.md"),
    )

    selector_client = _make_client(model, api_key)

    termination = MaxMessageTermination(max_messages=settings.debate_max_turns)

    team = SelectorGroupChat(
        participants=[skeptic, optimist, moderator],
        model_client=selector_client,
        termination_condition=termination,
        selector_prompt=(
            "You are the debate floor manager. Based on the conversation so far, "
            "choose the next speaker from {roles}. Ensure all voices are heard. "
            "The Moderator should intervene when the debate drifts or needs wrapping up. "
            "Current turn: {turns}. History:\n{history}"
        ),
    )

    research_summary = json.dumps(
        {
            "web_count": len(research_data.get("web", [])),
            "arxiv_count": len(research_data.get("arxiv", [])),
            "key_points": [r.get("title", "") for r in research_data.get("web", [])[:3]],
        }
    )

    task = (
        f"Topic: {topic}\n\n"
        f"Episode outline:\n{json.dumps(outline, indent=2)}\n\n"
        f"Research context: {research_summary}\n\n"
        "Produce a natural, engaging podcast debate. Each speaker should give 2-4 sentence "
        "responses. The Moderator introduces the topic, guides transitions, and wraps up."
    )

    result = await team.run(task=task)
    return _parse_messages(result.messages)
