"""Celery task: run the LangGraph episode generation pipeline."""

import asyncio
import os
from typing import Any

from .celery_app import celery_app


async def _run_pipeline(
    episode_id: str,
    show_id: str,
    topic: str,
    fmt: str,
    requires_human_approval: bool,
) -> dict[str, Any]:
    # Import here to avoid loading heavy deps at worker startup
    from podforge_agents.graphs.production_pipeline import create_pipeline
    from podforge_agents.graphs.state import initial_state

    db_url = os.environ.get(
        "AGENTS_DB_URL",
        "postgresql+psycopg://podforge:podforge@localhost:5432/podforge",
    )
    graph = await create_pipeline(db_url)

    state = initial_state(
        topic=topic,
        show_id=show_id,
        episode_id=episode_id,
        fmt=fmt,
        requires_human_approval=requires_human_approval,
    )
    config = {"configurable": {"thread_id": episode_id}}
    result: dict[str, Any] = await graph.ainvoke(state, config=config)
    return result


@celery_app.task(  # type: ignore[untyped-decorator]
    name="workers.generate_episode",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def generate_episode(
    self: Any,
    episode_id: str,
    show_id: str,
    topic: str,
    fmt: str = "debate",
    requires_human_approval: bool = False,
) -> dict[str, Any]:
    """Trigger the full LangGraph production pipeline for an episode."""
    try:
        return asyncio.run(_run_pipeline(episode_id, show_id, topic, fmt, requires_human_approval))
    except Exception as exc:
        raise self.retry(exc=exc) from exc
