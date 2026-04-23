"""Research summarisation chain — distils raw MCP data into a usable digest."""

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from ..config import get_settings
from ..llm import get_llm


async def summarise_research(topic: str, research_data: dict[str, Any]) -> str:
    """Return a concise research digest suitable for the outline chain."""
    settings = get_settings()
    llm = get_llm(model=settings.outline_model or None)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a research analyst preparing a brief for podcast hosts. "
                "Synthesise the provided research into a concise 300-word digest covering: "
                "key facts, competing perspectives, recent developments, and notable quotes. "
                "Be objective and balanced.",
            ),
            (
                "human",
                "Topic: {topic}\n\nRaw research:\n{research}",
            ),
        ]
    )
    web = research_data.get("web", [])[:5]
    arxiv = research_data.get("arxiv", [])[:3]
    news = research_data.get("news", [])[:5]
    raw = json.dumps({"web": web, "arxiv": arxiv, "news": news}, indent=2)
    response = await (prompt | llm).ainvoke({"topic": topic, "research": raw})
    return str(response.content)
