import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.dependencies import get_current_user
from podforge_api.database import get_db
from podforge_api.models.episode import Episode
from podforge_api.models.user import User
from podforge_api.schemas.episode import EpisodeCreate, EpisodeResponse, EpisodeUpdate

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("/", response_model=list[EpisodeResponse])
async def list_episodes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Episode]:
    result = await db.execute(select(Episode).limit(100))
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
    return episode


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Episode:
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return episode


@router.patch("/{episode_id}", response_model=EpisodeResponse)
async def update_episode(
    episode_id: uuid.UUID,
    body: EpisodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Episode:
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
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
    result = await db.execute(select(Episode).where(Episode.id == episode_id))
    episode = result.scalar_one_or_none()
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    await db.delete(episode)
