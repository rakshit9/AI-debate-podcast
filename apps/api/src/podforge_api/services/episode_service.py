"""Episode business logic — pipeline trigger, status, approval, publishing."""

import uuid
from typing import Any

import sqlalchemy as sa
from celery.result import AsyncResult
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.models.episode import Episode
from podforge_api.models.show import Show
from podforge_api.schemas.episode import EpisodeStatusResponse, ShowStatsResponse
from podforge_api.workers.celery_app import celery_app


class EpisodeService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Retrieval ─────────────────────────────────────────────────────────────

    async def get(self, episode_id: uuid.UUID) -> Episode | None:
        result = await self._db.execute(select(Episode).where(Episode.id == episode_id))
        return result.scalar_one_or_none()

    async def list_for_show(
        self,
        show_id: uuid.UUID,
        *,
        status: str | None = None,
        format_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Episode]:
        q = select(Episode).where(Episode.show_id == show_id)
        if status:
            q = q.where(Episode.status == status)
        if format_filter:
            q = q.where(Episode.format == format_filter)
        q = q.order_by(Episode.created_at.desc()).limit(limit).offset(offset)
        result = await self._db.execute(q)
        return list(result.scalars())

    # ── Pipeline trigger ──────────────────────────────────────────────────────

    async def queue_pipeline(
        self,
        episode: Episode,
        requires_human_approval: bool = False,
    ) -> str:
        """Kick off the Celery pipeline task and store the task_id on the episode."""
        from podforge_shared_types.enums import EpisodeStatusEnum

        task = celery_app.send_task(
            "workers.generate_episode",
            kwargs={
                "episode_id": str(episode.id),
                "show_id": str(episode.show_id),
                "topic": episode.topic,
                "fmt": episode.format,
                "requires_human_approval": requires_human_approval,
            },
        )
        episode.celery_task_id = task.id
        episode.status = EpisodeStatusEnum.PROCESSING
        await self._db.flush()
        return str(task.id)

    # ── Status ────────────────────────────────────────────────────────────────

    async def get_status(self, episode: Episode) -> EpisodeStatusResponse:
        celery_state = "UNKNOWN"
        error: str | None = None
        if episode.celery_task_id:
            result: AsyncResult = AsyncResult(episode.celery_task_id, app=celery_app)
            celery_state = result.state
            if result.failed():
                error = str(result.result)

        return EpisodeStatusResponse(
            episode_id=episode.id,
            status=episode.status,
            celery_state=celery_state,
            pipeline_progress=episode.pipeline_progress,
            error=error,
        )

    # ── Human approval gate ───────────────────────────────────────────────────

    async def send_approval(self, episode: Episode, decision: str) -> None:
        """Resume a paused LangGraph graph via Command(resume=decision)."""
        import os

        from langgraph.types import Command
        from podforge_agents.graphs.production_pipeline import create_pipeline

        db_url = os.environ.get(
            "AGENTS_DB_URL",
            "postgresql+psycopg://podforge:podforge@localhost:5432/podforge",
        )
        config = {"configurable": {"thread_id": str(episode.id)}}
        graph = await create_pipeline(db_url)
        await graph.ainvoke(Command(resume=decision), config=config)

    # ── Publishing ────────────────────────────────────────────────────────────

    async def publish(self, episode: Episode, show: Show) -> dict[str, Any]:
        """Trigger publish-mcp tools and update published_urls on the episode."""
        import datetime

        from podforge_publish_mcp.tools.rss import generate_rss_item
        from podforge_publish_mcp.tools.twitter import post_tweet
        from podforge_shared_types.enums import EpisodeStatusEnum

        published: dict[str, Any] = dict(episode.published_urls)

        # RSS item
        if episode.audio_url:
            try:
                rss_result: dict[str, Any] = await generate_rss_item(
                    title=episode.topic,
                    description=episode.transcript or episode.topic,
                    audio_url=episode.audio_url,
                    duration_seconds=episode.duration_seconds or 0,
                    episode_id=str(episode.id),
                )
                published["rss"] = rss_result.get("item_guid", "")
            except Exception:  # noqa: S110
                pass

        # Twitter announcement
        if episode.audio_url:
            try:
                tweet_text = f"New episode: {episode.topic} 🎙️ {episode.audio_url}"
                tweet_result: dict[str, Any] = await post_tweet(tweet_text)
                published["twitter"] = tweet_result.get("tweet_id", "")
            except Exception:  # noqa: S110
                pass

        episode.published_urls = published
        episode.published_at = datetime.datetime.now(datetime.UTC)
        episode.status = EpisodeStatusEnum.PUBLISHED
        await self._db.flush()
        return published

    # ── Show stats ────────────────────────────────────────────────────────────

    async def show_stats(self, show_id: uuid.UUID) -> ShowStatsResponse:
        from decimal import Decimal

        from podforge_shared_types.enums import EpisodeStatusEnum

        rows = await self._db.execute(
            select(
                func.count(Episode.id).label("total"),
                func.sum(
                    sa.cast(Episode.status == EpisodeStatusEnum.PUBLISHED, sa.Integer)
                ).label("published"),
                func.sum(
                    sa.cast(Episode.status == EpisodeStatusEnum.PROCESSING, sa.Integer)
                ).label("processing"),
                func.sum(
                    sa.cast(Episode.status == EpisodeStatusEnum.QUEUED, sa.Integer)
                ).label("queued"),
                func.coalesce(func.sum(Episode.duration_seconds), 0).label("total_duration"),
                func.coalesce(func.sum(Episode.cost_usd), Decimal("0")).label("total_cost"),
            ).where(Episode.show_id == show_id)
        )
        row = rows.one()

        return ShowStatsResponse(
            show_id=show_id,
            total_episodes=int(row.total or 0),
            published_episodes=int(row.published or 0),
            processing_episodes=int(row.processing or 0),
            queued_episodes=int(row.queued or 0),
            total_duration_seconds=int(row.total_duration or 0),
            total_cost_usd=Decimal(str(row.total_cost or "0")),
        )
