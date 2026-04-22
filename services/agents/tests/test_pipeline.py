"""Unit tests for the LangGraph pipeline nodes (all externals mocked)."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from podforge_agents.graphs.state import PipelineState, initial_state


def _make_state(**overrides: Any) -> PipelineState:
    base = initial_state(
        topic="Will AI replace software engineers?",
        show_id="show-001",
        episode_id="ep-001",
    )
    base.update(overrides)  # type: ignore[typeddict-item]
    return base


# ── planner_node ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_planner_node_adds_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    mock_response = MagicMock()
    mock_response.content = "Core tension: augmentation vs replacement."

    with patch("podforge_agents.nodes.planner.ChatAnthropic") as mock_llm_cls:
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm = MagicMock()
        mock_llm.__or__ = MagicMock(return_value=mock_chain)
        mock_llm_cls.return_value = mock_llm

        with patch("podforge_agents.nodes.planner.ChatPromptTemplate.from_messages") as mock_prompt:
            mock_prompt_inst = MagicMock()
            mock_prompt_inst.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt.return_value = mock_prompt_inst

            from podforge_agents.nodes.planner import planner_node

            result = await planner_node(_make_state())

    assert "plan" in result["research_data"]
    assert "augmentation" in result["research_data"]["plan"]


# ── research_node ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_research_node_fans_out() -> None:
    web = [{"title": "AI article", "url": "https://example.com"}]
    arxiv = [{"title": "AI paper", "authors": ["Alice"]}]
    news = [{"title": "AI news", "source": "BBC"}]

    with (
        patch(
            "podforge_agents.nodes.research.research_client.search_web",
            new_callable=AsyncMock,
            return_value=web,
        ),
        patch(
            "podforge_agents.nodes.research.research_client.fetch_arxiv",
            new_callable=AsyncMock,
            return_value=arxiv,
        ),
        patch(
            "podforge_agents.nodes.research.research_client.get_news_today",
            new_callable=AsyncMock,
            return_value=news,
        ),
    ):
        from podforge_agents.nodes.research import research_node

        result = await research_node(_make_state())

    assert result["research_data"]["web"] == web
    assert result["research_data"]["arxiv"] == arxiv
    assert result["research_data"]["news"] == news


# ── quality_gate_node ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_quality_gate_approves_good_outline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    mock_response = MagicMock()
    mock_response.content = '{"score": 9, "reason": "Strong debate potential."}'

    with patch("podforge_agents.nodes.quality_gate.ChatAnthropic") as mock_llm_cls:
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        with patch(
            "podforge_agents.nodes.quality_gate.ChatPromptTemplate.from_messages"
        ) as mock_prompt:
            mock_prompt_inst = MagicMock()
            mock_prompt_inst.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt.return_value = mock_prompt_inst

            from podforge_agents.nodes.quality_gate import quality_gate_node, quality_gate_router

            state = _make_state(outline={"intro": "Great intro", "points": []})
            result = await quality_gate_node(state)

    assert result["outline_approved"] is True
    updated = {**state, **result}
    assert quality_gate_router(updated) == "debate"  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_quality_gate_retries_poor_outline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    mock_response = MagicMock()
    mock_response.content = '{"score": 4, "reason": "Too vague."}'

    with patch("podforge_agents.nodes.quality_gate.ChatAnthropic") as mock_llm_cls:
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        with patch(
            "podforge_agents.nodes.quality_gate.ChatPromptTemplate.from_messages"
        ) as mock_prompt:
            mock_prompt_inst = MagicMock()
            mock_prompt_inst.__or__ = MagicMock(return_value=mock_chain)
            mock_prompt.return_value = mock_prompt_inst

            from podforge_agents.nodes.quality_gate import quality_gate_node, quality_gate_router

            state = _make_state(outline={"intro": "Vague"}, retry_count=0)
            result = await quality_gate_node(state)

    assert result["outline_approved"] is False
    assert result["retry_count"] == 1
    updated = {**state, **result}
    assert quality_gate_router(updated) == "outline"  # type: ignore[arg-type]


# ── fact_check_router ─────────────────────────────────────────────────────────


def test_fact_check_router_clean() -> None:
    from podforge_agents.nodes.fact_check import fact_check_router

    state = _make_state(script_clean=True)
    assert fact_check_router(state) == "tts"


def test_fact_check_router_needs_correction() -> None:
    from podforge_agents.nodes.fact_check import fact_check_router

    state = _make_state(script_clean=False)
    assert fact_check_router(state) == "correction"


# ── state helpers ─────────────────────────────────────────────────────────────


def test_initial_state_defaults() -> None:
    state = initial_state("Topic", "show-1", "ep-1")
    assert state["topic"] == "Topic"
    assert state["retry_count"] == 0
    assert state["script"] == []
    assert state["outline_approved"] is False
    assert state["requires_human_approval"] is False


# ── pipeline graph wiring ─────────────────────────────────────────────────────


def test_pipeline_compiles_without_checkpointer() -> None:
    from podforge_agents.graphs.production_pipeline import create_pipeline_no_checkpoint

    graph = create_pipeline_no_checkpoint()
    assert graph is not None
    # Verify all nodes are registered
    node_names = set(graph.nodes.keys())
    assert "planner" in node_names
    assert "debate" in node_names
    assert "tts" in node_names
    assert "publish" in node_names
