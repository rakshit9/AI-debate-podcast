"""AutoGen SelectorGroupChat panel — host + 3 panelists with distinct stances."""

import json
from pathlib import Path
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.anthropic import AnthropicChatCompletionClient

from ..config import get_settings
from ..graphs.state import ScriptLine

_PROMPTS = Path(__file__).parent.parent / "prompts" / "hosts"

_PANELIST_STANCES = [
    ("PanelistA", "You represent the optimistic / pro-technology perspective."),
    ("PanelistB", "You represent the skeptical / risk-aware perspective."),
    ("PanelistC", "You represent the pragmatic / policy-focused perspective."),
]


def _read(name: str) -> str:
    return (_PROMPTS / name).read_text()


def _make_client(model: str, api_key: str) -> AnthropicChatCompletionClient:
    return AnthropicChatCompletionClient(model=model, api_key=api_key)


def _parse_messages(messages: Any) -> list[ScriptLine]:
    script: list[ScriptLine] = []
    agent_names = {"Moderator", "PanelistA", "PanelistB", "PanelistC"}
    for msg in messages:
        source = getattr(msg, "source", None) or getattr(msg, "name", None)
        content = getattr(msg, "content", None)
        if source in agent_names and content:
            text = content if isinstance(content, str) else str(content)
            text = text.strip()
            if text:
                script.append(ScriptLine(speaker=str(source), text=text))
    return script


async def run_panel(
    topic: str,
    outline: dict[str, Any],
    research_data: dict[str, Any],
) -> list[ScriptLine]:
    """Run a 4-agent SelectorGroupChat panel and return the structured script."""
    settings = get_settings()
    model = settings.debate_model
    api_key = settings.anthropic_api_key

    panelist_prompt = _read("panelist_v1.md")
    panelists = [
        AssistantAgent(
            name=name,
            model_client=_make_client(model, api_key),
            system_message=f"{panelist_prompt}\n\n## Your Specific Stance\n{stance}",
        )
        for name, stance in _PANELIST_STANCES
    ]
    moderator = AssistantAgent(
        name="Moderator",
        model_client=_make_client(model, api_key),
        system_message=_read("moderator_v1.md"),
    )

    selector_client = _make_client(model, api_key)
    max_turns = settings.debate_max_turns + 4
    termination = MaxMessageTermination(max_messages=max_turns)

    team = SelectorGroupChat(
        participants=[moderator, *panelists],
        model_client=selector_client,
        termination_condition=termination,
        selector_prompt=(
            "You manage a panel discussion. Choose the next speaker from {roles}. "
            "Give each panelist roughly equal airtime. The Moderator should guide topic "
            "transitions and keep the discussion on track. "
            "Current turn: {turns}. History:\n{history}"
        ),
    )

    research_summary = json.dumps(
        {"key_points": [r.get("title", "") for r in research_data.get("web", [])[:5]]}
    )
    task = (
        f"Topic: {topic}\n\n"
        f"Episode outline:\n{json.dumps(outline, indent=2)}\n\n"
        f"Research context: {research_summary}\n\n"
        "The Moderator opens the panel, introduces each panelist briefly, then facilitates "
        "a structured discussion hitting each point in the outline. Wrap up with a synthesis."
    )

    result = await team.run(task=task)
    return _parse_messages(result.messages)
