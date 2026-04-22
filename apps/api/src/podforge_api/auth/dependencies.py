import uuid

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from podforge_api.auth.jwt import InvalidTokenError, decode_token
from podforge_api.auth.password import verify_password
from podforge_api.config import Settings, get_settings
from podforge_api.database import get_db
from podforge_api.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    if token:
        try:
            payload = decode_token(token, settings)
        except InvalidTokenError:
            raise _401
        if payload.type != "access":
            raise _401
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(payload.sub), User.is_active.is_(True))
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise _401
        return user

    if api_key:
        result = await db.execute(select(User).where(User.api_key_hash.is_not(None)))
        for candidate in result.scalars():
            if candidate.api_key_hash and verify_password(api_key, candidate.api_key_hash):
                if not candidate.is_active:
                    raise _401
                return candidate

    raise _401
