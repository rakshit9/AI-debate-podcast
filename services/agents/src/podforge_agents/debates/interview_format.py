"""AutoGen RoundRobinGroupChat interview — host + expert guest."""

import json
from pathlib import Path
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat

from ..config import get_settings
from ..graphs.state import ScriptLine
from ..llm import get_autogen_client

_PROMPTS = Path(__file__).parent.parent / "prompts" / "hosts"


def _read(name: str) -> str:
    return (_PROMPTS / name).read_text()


def _parse_messages(messages: Any) -> list[ScriptLine]:
    script: list[ScriptLine] = []
    agent_names = {"Interviewer", "Guest"}
    for msg in messages:
        source = getattr(msg, "source", None) or getattr(msg, "name", None)
        content = getattr(msg, "content", None)
        if source in agent_names and content:
            text = content if isinstance(content, str) else str(content)
            text = text.strip()
            if text:
                script.append(ScriptLine(speaker=str(source), text=text))
    return script


async def run_interview(
    topic: str,
    outline: dict[str, Any],
    research_data: dict[str, Any],
) -> list[ScriptLine]:
    """Run a 2-agent round-robin interview and return the structured script."""
    settings = get_settings()
    model = settings.debate_model or None

    interviewer = AssistantAgent(
        name="Interviewer",
        model_client=get_autogen_client(model),
        system_message=_read("interviewer_v1.md"),
    )
    guest = AssistantAgent(
        name="Guest",
        model_client=get_autogen_client(model),
        system_message=_read("guest_v1.md"),
    )

    max_turns = max(6, settings.debate_max_turns - 2)
    termination = MaxMessageTermination(max_messages=max_turns)
    team = RoundRobinGroupChat(
        participants=[interviewer, guest],
        termination_condition=termination,
    )

    research_summary = json.dumps(
        {"key_points": [r.get("title", "") for r in research_data.get("web", [])[:5]]}
    )
    task = (
        f"Topic: {topic}\n\n"
        f"Episode outline:\n{json.dumps(outline, indent=2)}\n\n"
        f"Research context: {research_summary}\n\n"
        "The Interviewer opens by introducing the topic and asking the first question. "
        "The Guest answers. Continue for a natural, in-depth interview."
    )

    result = await team.run(task=task)
    return _parse_messages(result.messages)
