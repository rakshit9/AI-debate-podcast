import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.models.user import User
from podforge_api.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None:
        uid = uuid.UUID(str(user_id))
        result = await self._db.execute(select(User).where(User.id == uid))
        return result.scalar_one_or_none()

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def set_api_key(self, user_id: uuid.UUID, hashed_key: str | None) -> None:
        user = await self.get_by_id(user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")
        user.api_key_hash = hashed_key
        await self._db.flush()
