import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.dependencies import get_current_user
from podforge_api.database import get_db
from podforge_api.models.host import Host
from podforge_api.models.user import User
from podforge_api.schemas.host import HostCreate, HostResponse, HostUpdate

router = APIRouter(prefix="/hosts", tags=["hosts"])


@router.get("/", response_model=list[HostResponse])
async def list_hosts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Host]:
    result = await db.execute(select(Host))
    return list(result.scalars())


@router.post("/", response_model=HostResponse, status_code=status.HTTP_201_CREATED)
async def create_host(
    body: HostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Host:
    host = Host(
        name=body.name,
        personality_prompt=body.personality_prompt,
        voice_id=body.voice_id,
        voice_provider=body.voice_provider,
        temperature=body.temperature,
        model=body.model,
    )
    db.add(host)
    await db.flush()
    await db.refresh(host)
    return host


@router.get("/{host_id}", response_model=HostResponse)
async def get_host(
    host_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Host:
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return host


@router.patch("/{host_id}", response_model=HostResponse)
async def update_host(
    host_id: uuid.UUID,
    body: HostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Host:
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(host, field, value)
    await db.flush()
    await db.refresh(host)
    return host


@router.delete("/{host_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_host(
    host_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalar_one_or_none()
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    await db.delete(host)
