import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.dependencies import get_current_user
from podforge_api.database import get_db
from podforge_api.models.show import Show
from podforge_api.models.user import User
from podforge_api.schemas.show import ShowCreate, ShowResponse, ShowUpdate

router = APIRouter(prefix="/shows", tags=["shows"])


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


@router.get("/{show_id}", response_model=ShowResponse)
async def get_show(
    show_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Show:
    result = await db.execute(
        select(Show).where(Show.id == show_id, Show.owner_id == current_user.id)
    )
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return show


@router.patch("/{show_id}", response_model=ShowResponse)
async def update_show(
    show_id: uuid.UUID,
    body: ShowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Show:
    result = await db.execute(
        select(Show).where(Show.id == show_id, Show.owner_id == current_user.id)
    )
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
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
    result = await db.execute(
        select(Show).where(Show.id == show_id, Show.owner_id == current_user.id)
    )
    show = result.scalar_one_or_none()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    await db.delete(show)
