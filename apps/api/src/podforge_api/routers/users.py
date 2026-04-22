from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.dependencies import get_current_user
from podforge_api.database import get_db
from podforge_api.models.user import User
from podforge_api.schemas.user import UserResponse, UserUpdate
from podforge_api.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    svc = UserService(db)
    return await svc.update(current_user.id, body)
