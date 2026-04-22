"""Celery task: run the LangGraph episode generation pipeline."""

import asyncio
import json
import os
from typing import Any

import redis.asyncio as aioredis

from .celery_app import celery_app

_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


async def _publish_progress(
    episode_id: str,
    node: str,
    event_type: str = "node_complete",
    extra: dict[str, Any] | None = None,
) -> None:
    client: aioredis.Redis = aioredis.from_url(_REDIS_URL)  # type: ignore[no-untyped-call]
    try:
        payload = json.dumps(
            {"type": event_type, "node": node, "episode_id": episode_id, **(extra or {})}
        )
        await client.publish(f"podforge:episode:{episode_id}:progress", payload)
    finally:
        await client.aclose()


async def _run_pipeline(
    episode_id: str,
    show_id: str,
    topic: str,
    fmt: str,
    requires_human_approval: bool,
) -> dict[str, Any]:
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

    await _publish_progress(episode_id, "start", event_type="started")

    result: dict[str, Any] = {}
    async for event in graph.astream_events(state, config=config, version="v2"):
        kind = event.get("event", "")
        if kind == "on_chain_end":
            node_name: str = event.get("name", "")
            if node_name and node_name not in ("LangGraph", "__start__"):
                await _publish_progress(episode_id, node_name)
        elif kind == "on_chain_error":
            await _publish_progress(
                episode_id,
                event.get("name", "unknown"),
                event_type="error",
                extra={"error": str(event.get("data", {}).get("error", ""))},
            )

    # Retrieve final state from last event
    final_state = await graph.aget_state(config)
    if final_state and final_state.values:
        result = dict(final_state.values)

    await _publish_progress(episode_id, "pipeline", event_type="completed")
    return result


async def _update_episode_from_result(
    episode_id: str,
    result: dict[str, Any],
) -> None:
    """Persist final pipeline state back to Postgres."""
    from decimal import Decimal

    from podforge_shared_types.enums import EpisodeStatusEnum
    from sqlalchemy import select

    from podforge_api.database import AsyncSessionLocal
    from podforge_api.models.episode import Episode

    async with AsyncSessionLocal() as db:
        ep_result = await db.execute(select(Episode).where(Episode.id == episode_id))
        episode = ep_result.scalar_one_or_none()
        if not episode:
            return

        episode.script = result.get("script", [])
        episode.audio_url = result.get("final_audio_url")
        episode.transcript = result.get("transcript")
        episode.published_urls = result.get("published_urls", {})
        episode.status = (
            EpisodeStatusEnum.PUBLISHED if episode.audio_url else EpisodeStatusEnum.PROCESSING
        )
        episode.pipeline_progress = {"completed": True, "nodes_run": list(result.keys())}

        if result.get("audio_segments"):
            total_dur = sum(int(seg.get("duration_seconds", 0)) for seg in result["audio_segments"])
            episode.duration_seconds = total_dur

        episode.cost_usd = Decimal("0")
        await db.commit()


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
        result = asyncio.run(
            _run_pipeline(episode_id, show_id, topic, fmt, requires_human_approval)
        )
        asyncio.run(_update_episode_from_result(episode_id, result))
        return result
    except Exception as exc:
        asyncio.run(
            _publish_progress(episode_id, "pipeline", event_type="error", extra={"error": str(exc)})
        )
        raise self.retry(exc=exc) from exc
