"""LangGraph production pipeline — the full episode generation state machine."""

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ..nodes.approval_gate import approval_gate_node, approval_gate_router
from ..nodes.correction import correction_node
from ..nodes.debate import debate_node
from ..nodes.fact_check import fact_check_node, fact_check_router
from ..nodes.memory_update import memory_update_node
from ..nodes.mix import mix_node
from ..nodes.outline import outline_node
from ..nodes.planner import planner_node
from ..nodes.publish import publish_node
from ..nodes.quality_gate import quality_gate_node, quality_gate_router
from ..nodes.research import research_node
from ..nodes.tts import tts_node
from .state import PipelineState


def _build_graph() -> StateGraph:  # type: ignore[type-arg]
    builder: StateGraph = StateGraph(PipelineState)  # type: ignore[type-arg]

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("planner", planner_node)
    builder.add_node("research", research_node)
    builder.add_node("outline", outline_node)
    builder.add_node("quality_gate", quality_gate_node)
    builder.add_node("debate", debate_node)
    builder.add_node("fact_check", fact_check_node)
    builder.add_node("correction", correction_node)
    builder.add_node("tts", tts_node)
    builder.add_node("mix", mix_node)
    builder.add_node("approval_gate", approval_gate_node)
    builder.add_node("publish", publish_node)
    builder.add_node("memory_update", memory_update_node)

    # ── Linear edges ─────────────────────────────────────────────────────────
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "research")
    builder.add_edge("research", "outline")
    builder.add_edge("outline", "quality_gate")
    builder.add_edge("debate", "fact_check")
    builder.add_edge("correction", "tts")
    builder.add_edge("tts", "mix")
    builder.add_edge("mix", "approval_gate")
    builder.add_edge("publish", "memory_update")
    builder.add_edge("memory_update", END)

    # ── Conditional edges ─────────────────────────────────────────────────────
    builder.add_conditional_edges(
        "quality_gate",
        quality_gate_router,
        {"outline": "outline", "debate": "debate"},
    )
    builder.add_conditional_edges(
        "fact_check",
        fact_check_router,
        {"correction": "correction", "tts": "tts"},
    )
    builder.add_conditional_edges(
        "approval_gate",
        approval_gate_router,
        {"publish": "publish", "__end__": END},
    )

    return builder


async def create_pipeline(db_url: str) -> CompiledStateGraph:  # type: ignore[type-arg]
    """Build and compile the pipeline with PostgreSQL checkpointing."""
    async with AsyncPostgresSaver.from_conn_string(db_url) as checkpointer:
        await checkpointer.setup()
        return _build_graph().compile(checkpointer=checkpointer)


def create_pipeline_no_checkpoint() -> CompiledStateGraph:  # type: ignore[type-arg]
    """Build the pipeline without checkpointing (for testing)."""
    return _build_graph().compile()
