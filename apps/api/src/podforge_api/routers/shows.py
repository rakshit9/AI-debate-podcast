"""Show endpoints — CRUD + RSS feed + stats."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.dependencies import get_current_user
from podforge_api.database import get_db
from podforge_api.models.episode import Episode
from podforge_api.models.show import Show
from podforge_api.models.user import User
from podforge_api.schemas.episode import ShowStatsResponse
from podforge_api.schemas.show import ShowCreate, ShowResponse, ShowUpdate
from podforge_api.services.episode_service import EpisodeService

router = APIRouter(prefix="/shows", tags=["shows"])


async def _get_show_or_404(
    show_id: uuid.UUID,
    db: AsyncSession,
    current_user: User,
) -> Show:
    result = await db.execute(
        select(Show).where(Show.id == show_id, Show.owner_id == current_user.id)
    )
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return show


# ── Collection ────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[ShowResponse])
async def list_shows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Show]:
    result = await db.execute(select(Show).where(Show.owner_id == current_user.id))
    return list(result.scalars())


@router.post("/", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
async def create_show(
    body: ShowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Show:
    show = Show(
        owner_id=current_user.id,
        name=body.name,
        description=body.description,
        style_guide=body.style_guide,
        default_format=body.default_format,
        host_ids=body.host_ids,
        rss_feed_url=body.rss_feed_url,
        artwork_url=body.artwork_url,
    )
    db.add(show)
    await db.flush()
    await db.refresh(show)
    return show


# ── Single show ───────────────────────────────────────────────────────────────


@router.get("/{show_id}", response_model=ShowResponse)
async def get_show(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Show:
    return await _get_show_or_404(show_id, db, current_user)


@router.patch("/{show_id}", response_model=ShowResponse)
async def update_show(
    show_id: uuid.UUID,
    body: ShowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Show:
    show = await _get_show_or_404(show_id, db, current_user)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(show, field, value)
    await db.flush()
    await db.refresh(show)
    return show


@router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    show = await _get_show_or_404(show_id, db, current_user)
    await db.delete(show)


# ── Stats ─────────────────────────────────────────────────────────────────────


@router.get("/{show_id}/stats", response_model=ShowStatsResponse)
async def show_stats(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShowStatsResponse:
    await _get_show_or_404(show_id, db, current_user)
    return await EpisodeService(db).show_stats(show_id)


# ── RSS feed ──────────────────────────────────────────────────────────────────


@router.get("/{show_id}/rss.xml")
async def rss_feed(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Dynamically generate a podcast RSS feed for the show."""
    result = await db.execute(select(Show).where(Show.id == show_id))
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")

    episodes_result = await db.execute(
        select(Episode)
        .where(Episode.show_id == show_id, Episode.audio_url.isnot(None))
        .order_by(Episode.published_at.desc())
        .limit(100)
    )
    episodes = list(episodes_result.scalars())

    try:
        from podforge_publish_mcp.tools.rss import generate_rss_feed

        feed_xml: str = await generate_rss_feed(
            show_id=str(show_id),
            title=show.name,
            description=show.description or show.name,
            artwork_url=show.artwork_url or "",
            episodes=[
                {
                    "id": str(ep.id),
                    "title": ep.topic,
                    "description": ep.transcript or ep.topic,
                    "audio_url": ep.audio_url or "",
                    "duration_seconds": ep.duration_seconds or 0,
                    "published_at": ep.published_at.isoformat() if ep.published_at else "",
                }
                for ep in episodes
            ],
        )
        return Response(content=feed_xml, media_type="application/rss+xml")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"RSS generation failed: {exc}",
        ) from exc
