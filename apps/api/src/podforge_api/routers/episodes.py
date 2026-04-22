"""Episode endpoints — CRUD + pipeline control + SSE streaming."""

import asyncio
import json
import uuid
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.dependencies import get_current_user
from podforge_api.config import get_settings
from podforge_api.database import get_db
from podforge_api.models.episode import Episode
from podforge_api.models.user import User
from podforge_api.schemas.episode import (
    EpisodeApproveRequest,
    EpisodeCreate,
    EpisodeResponse,
    EpisodeStatusResponse,
    EpisodeUpdate,
)
from podforge_api.services.episode_service import EpisodeService

router = APIRouter(prefix="/episodes", tags=["episodes"])


def _svc(db: AsyncSession) -> EpisodeService:
    return EpisodeService(db)


async def _get_episode_or_404(
    episode_id: uuid.UUID,
    db: AsyncSession,
) -> Episode:
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return episode


# ── Collection ────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[EpisodeResponse])
async def list_episodes(
    show_id: uuid.UUID | None = Query(default=None),
    episode_status: str | None = Query(default=None, alias="status"),
    format: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Episode]:
    if show_id:
        return await _svc(db).list_for_show(
            show_id,
            status=episode_status,
            format_filter=format,
            limit=limit,
            offset=offset,
        )
    q = select(Episode).order_by(Episode.created_at.desc()).limit(limit).offset(offset)
    if episode_status:
        q = q.where(Episode.status == episode_status)
    if format:
        q = q.where(Episode.format == format)
    result = await db.execute(q)
    return list(result.scalars())


@router.post("/", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
async def create_episode(
    body: EpisodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Episode:
    episode = Episode(show_id=body.show_id, topic=body.topic, format=body.format)
    db.add(episode)
    await db.flush()
    await db.refresh(episode)
    await _svc(db).queue_pipeline(episode, requires_human_approval=body.requires_human_approval)
    await db.refresh(episode)
    return episode


# ── Single episode ────────────────────────────────────────────────────────────


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Episode:
    return await _get_episode_or_404(episode_id, db)


@router.patch("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_id: uuid.UUID,
    body: EpisodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Episode:
    episode = await _get_episode_or_404(episode_id, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(episode, field, value)
    await db.flush()
    await db.refresh(episode)
    return episode


@router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    episode = await _get_episode_or_404(episode_id, db)
    await db.delete(episode)


# ── Pipeline control ──────────────────────────────────────────────────────────


@router.post("/{episode_id}/generate", response_model=EpisodeResponse)
async def generate_episode(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Episode:
    """Re-trigger generation for a queued or failed episode."""
    episode = await _get_episode_or_404(episode_id, db)
    await _svc(db).queue_pipeline(episode, requires_human_approval=False)
    await db.refresh(episode)
    return episode


@router.get("/{episode_id}/status", response_model=EpisodeStatusResponse)
async def get_episode_status(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EpisodeStatusResponse:
    episode = await _get_episode_or_404(episode_id, db)
    return await _svc(db).get_status(episode)


@router.post("/{episode_id}/approve", status_code=status.HTTP_202_ACCEPTED)
async def approve_episode(
    episode_id: uuid.UUID,
    body: EpisodeApproveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    episode = await _get_episode_or_404(episode_id, db)
    await _svc(db).send_approval(episode, body.decision)
    return {"detail": f"Approval '{body.decision}' sent"}


@router.post("/{episode_id}/publish", status_code=status.HTTP_202_ACCEPTED)
async def publish_episode(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    episode = await _get_episode_or_404(episode_id, db)
    if not episode.show:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Show not loaded")
    published = await _svc(db).publish(episode, episode.show)
    return {"detail": "Published", "published_urls": published}


# ── SSE streaming ─────────────────────────────────────────────────────────────


@router.get("/{episode_id}/stream")
async def stream_episode_progress(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Server-sent events stream of pipeline progress for an episode."""
    await _get_episode_or_404(episode_id, db)
    settings = get_settings()
    redis_url = str(settings.redis_url)

    async def _event_generator() -> Any:
        client: aioredis.Redis = aioredis.from_url(redis_url, decode_responses=True)  # type: ignore[no-untyped-call]
        channel = f"podforge:episode:{episode_id}:progress"
        pubsub = client.pubsub()
        try:
            await pubsub.subscribe(channel)
            yield f"data: {json.dumps({'type': 'connected', 'episode_id': str(episode_id)})}\n\n"
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield f"data: {message['data']}\n\n"
                    data = json.loads(message["data"])
                    if data.get("type") in ("completed", "error"):
                        break
                await asyncio.sleep(0)
        finally:
            await pubsub.unsubscribe(channel)
            await client.aclose()

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
